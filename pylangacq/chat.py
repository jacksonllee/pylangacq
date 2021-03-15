"""Interfacing with CHAT data files."""

import collections
import concurrent.futures as cf
import contextlib
import dataclasses
import datetime
import functools
import itertools
import os
import re
import shutil
import tempfile
import uuid
import warnings
import zipfile
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dateutil.parser import parse as parse_date
from dateutil.parser import ParserError

from pylangacq.measures import _CLITIC, _get_ipsyn, _get_mlum, _get_mluw, _get_ttr
from pylangacq.objects import Gra, Token, Utterance


_ENCODING = "utf-8"

_CHAT_EXTENSION = ".cha"

_TIMER_MARKS_REGEX = re.compile(r"\x15-?(\d+)_(\d+)-?\x15")


def _params_in_docstring(*params, class_method=True):
    docstring = ""

    if "participants" in params:
        docstring += """
        participants : str or iterable of str, optional
            Participants of interest. You may pass in a string (e.g., ``"CHI"``
            for studying child speech)
            or an iterable of strings (e.g., ``{"MOT", "INV"}``). Only the specified
            participants are included.
            If you pass in ``None`` (the default), all participants are included.
            This parameter cannot be used together with ``exclude``.
        exclude : str or iterable of str, optional
            Participants to exclude. You may pass in a string (e.g., ``"CHI"``
            for child-directed speech)
            or an iterable of strings (e.g., ``{"MOT", "INV"}``). Only the specified
            participants are excluded.
            If you pass in ``None`` (the default), no participants are excluded.
            This parameter cannot be used together with ``participants``."""

    if "by_utterances" in params:
        docstring += """
        by_utterances : bool, optional
            If ``True``, the resulting objects are wrapped as a list at the utterance
            level.
            If ``False`` (the default), such utterance-level list structure
            does not exist."""

    if "by_files" in params:
        docstring += """
        by_files : bool, optional
            If ``True``, return a list X of results, where len(X) is the number of
            files in the ``Reader`` object, and each element in X is the result for one
            file; the ordering of X corresponds to that of the file paths from
            :func:`~pylangacq.Reader.file_paths`.
            If ``False`` (the default), return the result that collapses the file
            distinction just described for when ``by_files`` is ``True``."""

    if "keep_case" in params:
        docstring += """
        keep_case : bool, optional
            If ``True`` (the default), case distinctions are kept, e.g.,
            word tokens like "the" and "The" are treated as distinct.
            If ``False``, all word tokens are forced to be in lowercase
            as a preprocessing step.
            CHAT data from CHILDES intentionally does not follow the orthographic
            convention of capitalizing the first letter of a sentence in the
            transcriptions (as would have been done in many European languages),
            and so leaving keep_case as True is appropriate in most cases."""

    if "match" in params:
        docstring += """
        match : str, optional
            If provided, only the file paths that match this string
            (by regular expression matching) are read and parsed.
            For example, to work with the American English dataset Brown (containing
            data for the children Adam, Eve, and Sarah),
            you can pass in ``"Eve"`` here to only handle the data for Eve, since
            the unzipped Brown data from CHILDES is in a directory structure of
            ``Brown/Eve/xxx.cha`` for Eve's data.
            If this parameter is not specified or ``None`` is passed in (the default),
            such file path filtering does not apply.
        exclude : str, optional
            If provided, the file paths that match this string (by regular expression
            matching) are excluded for reading and parsing."""

    if "allow_remote" in params:
        docstring += """
        allow_remote : bool, optional
            If ``True`` (the default), and if the data source looks like a URL,
            downloading the data from the internet will be attempted."""

    if "encoding" in params:
        docstring += """
        encoding : str, optional
            Text encoding to parse the CHAT data. The default value is ``"utf-8"``
            for Unicode UTF-8."""

    if "extension" in params:
        docstring += """
        extension : str, optional
            File extension for CHAT data files. The default value is ``".cha"``."""

    if "cls" in params:
        docstring += """
        cls : type, optional
            Either :class:`~pylangacq.chat.Reader` (the default),
            or a subclass from it that expects the same arguments for the methods
            :func:`~pylangacq.Reader.from_zip`, :func:`~pylangacq.Reader.from_dir`,
            and :func:`~pylangacq.Reader.from_files`.
            Pass in your own :class:`~pylangacq.chat.Reader` subclass
            for new or modified behavior of the returned reader object."""

    if not class_method:
        docstring = docstring.replace("\n        ", "\n    ")

    def real_decorator(func):
        if class_method:
            returns_header = "\n\n        Returns\n        -------"
        else:
            returns_header = "\n\n    Returns\n    -------"
        func.__doc__ = func.__doc__.replace(returns_header, docstring + returns_header)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return real_decorator


def _deprecate_warning(what, since_version, use_instead):
    """Throws a FutureWarning for deprecation.

    FutureWarning is used instead of DeprecationWarning, because Python
    does not show DeprecationWarning by default.

    Parameters
    ----------
    what : str
        What to deprecate.
    since_version : str
        Version "x.y.z" since which the deprecation is in effect.
    use_instead : str
        Use this instead.
    """
    warnings.warn(
        f"'{what}' has been deprecated since PyLangAcq v{since_version}. "
        f"Please use {use_instead} instead.",
        FutureWarning,
    )


@dataclasses.dataclass
class _File:
    """A CHAT file (or string).

    Attributes
    ----------
    file_path : str
    header : dict
    utterances : List[Utterance]
    """

    __slots__ = ("file_path", "header", "utterances")

    file_path: str
    header: Dict
    utterances: List[Utterance]


class Reader:
    """A reader that handles CHAT data."""

    def __init__(self):
        """Initialize an empty reader."""
        self._files = collections.deque()

    def _parse_chat_strs(self, strs: List[str], file_paths: List[str]) -> None:
        with cf.ProcessPoolExecutor() as executor:
            self._files = collections.deque(
                executor.map(self._parse_chat_str, strs, file_paths)
            )

    def __len__(self):
        raise NotImplementedError(
            "__len__ of a CHAT reader is intentionally undefined. "
            "Intuitively, there are different lengths one may refer to: "
            "Number of files in this reader? Utterances? Words? Something else?"
        )

    def _get_reader_from_files(self, files: Iterable[_File]):
        reader = self.__class__()
        reader._files = collections.deque(files)
        return reader

    def __iter__(self):
        yield from (self._get_reader_from_files([f]) for f in self._files)

    def __getitem__(self, item):
        if type(item) == int:
            return self._get_reader_from_files([self._files[item]])
        elif type(item) == slice:
            start, stop, step = item.indices(len(self._files))
            # Slicing of a list etc would give us a _shallow_ copy of the container,
            # and so we follow the shallow copying practice here for the files.
            return self._get_reader_from_files(
                itertools.islice(self._files.copy(), start, stop, step)
            )
        else:
            raise TypeError(
                f"Reader indices must be integers or slices, not {type(item)}"
            )

    def __setitem__(self, key, value):
        raise NotImplementedError(
            "Mutating the CHAT reader by targeting the individual files through "
            "indices is not supported. Please use the implemented Reader object "
            "methods to add or remove data."
        )

    def clear(self) -> None:
        """Remove all data from this reader."""
        self._files = collections.deque()

    def _append(self, left_or_right, reader: "Reader") -> None:
        func = "extendleft" if left_or_right == "left" else "extend"
        if type(reader) != Reader:
            raise TypeError(f"not a Reader object: {type(reader)}")
        getattr(self._files, func)(reader._files)

    def append(self, reader: "Reader") -> None:
        """Append data from another reader.

        New data is appended as-is with no filtering of any sort,
        even for files whose file paths duplicate those already in the current reader.

        Parameters
        ----------
        reader : Reader
            A reader from which to append data
        """
        self._append("right", reader)

    def append_left(self, reader: "Reader") -> None:
        """Left-append data from another reader.

        New data is appended as-is with no filtering of any sort,
        even for files whose file paths duplicate those already in the current reader.

        Parameters
        ----------
        reader : Reader
            A reader from which to left-append data
        """
        self._append("left", reader)

    def _extend(self, left_or_right, readers: "Iterable[Reader]") -> None:
        # Loop through each object in ``readers`` explicitly, so that we have
        # a chance to check that the object is indeed a Reader instance.
        new_files = []
        for reader in readers:
            if type(reader) != Reader:
                raise TypeError(f"not a Reader object: {type(reader)}")
            new_files.extend(reader._files)
        func = "extendleft" if left_or_right == "left" else "extend"
        getattr(self._files, func)(new_files)

    def extend(self, readers: "Iterable[Reader]") -> None:
        """Extend data from other readers.

        New data is appended as-is with no filtering of any sort,
        even for files whose file paths duplicate those already in the current reader.

        Parameters
        ----------
        readers : Iterable[Reader]
            Readers from which to extend data
        """
        # Loop through each object in ``readers`` explicitly, so that we have
        # a chance to check that the object is indeed a Reader instance.
        self._extend("right", readers)

    def extend_left(self, readers: "Iterable[Reader]") -> None:
        """Left-extend data from other readers.

        New data is appended as-is with no filtering of any sort,
        even for files whose file paths duplicate those already in the current reader.

        Parameters
        ----------
        readers : Iterable[Reader]
            Readers from which to extend data
        """
        self._extend("left", readers)

    def _pop(self, left_or_right) -> "Reader":
        func = "popleft" if left_or_right == "left" else "pop"
        file_ = getattr(self._files, func)()
        return self._get_reader_from_files([file_])

    def pop(self) -> "Reader":
        """Drop the last data file from the reader and return it as a reader.

        Returns
        -------
        Reader
        """
        return self._pop("right")

    def pop_left(self) -> "Reader":
        """Drop the first data file from the reader and return it as a reader.

        Returns
        -------
        Reader
        """
        return self._pop("left")

    @staticmethod
    def _flatten(item_type, nested) -> Union[List, Set]:
        if item_type == list:
            return [item for items in nested for item in items]
        elif item_type == int:
            return sum(nested)
        elif item_type == set:
            return set().union(*nested)
        elif item_type == collections.Counter:
            return sum(nested, collections.Counter())
        else:
            raise ValueError(f"unrecognized item type: {item_type}")

    @_params_in_docstring("participants", "exclude", "by_files")
    def utterances(
        self, participants=None, exclude=None, by_files=False
    ) -> Union[List[Utterance], List[List[Utterance]]]:
        """Return the utterances.

        Parameters
        ----------

        Returns
        -------
        List[Utterance] if ``by_files`` is ``False``, otherwise List[List[Utterance]]
        """
        result_by_files = self._filter_utterances_by_participants(participants, exclude)
        if by_files:
            return result_by_files
        else:
            return self._flatten(list, result_by_files)

    def _get_result_by_utterances_by_files(self, result, by_utterances, by_files):
        if by_files and by_utterances:
            pass
        elif by_files and not by_utterances:
            result = [self._flatten(list, f) for f in result]
        elif not by_files and by_utterances:
            result = self._flatten(list, result)
        else:
            # not by_files and not by_utterances
            result = self._flatten(list, (self._flatten(list, f) for f in result))
        return result

    @_params_in_docstring("participants", "exclude", "by_utterances", "by_files")
    def tokens(
        self, participants=None, exclude=None, by_utterances=False, by_files=False
    ) -> Union[List[Token], List[List[Token]], List[List[List[Token]]]]:
        """Return the tokens.

        Parameters
        ----------

        Returns
        -------
        List[List[List[Token]]] if both ``by_utterances`` and ``by_files`` are ``True``
        List[List[Token]] if ``by_utterances`` is ``True`` and ``by_files`` is ``False``
        List[List[Token]] if ``by_utterances`` is ``False`` and ``by_files`` is ``True``
        List[Token] if both ``by_utterances`` and ``by_files`` are ``False``
        """
        utterances = self.utterances(
            participants=participants, exclude=exclude, by_files=True
        )
        result = [[u.tokens for u in us] for us in utterances]
        return self._get_result_by_utterances_by_files(result, by_utterances, by_files)

    @_params_in_docstring("participants", "exclude", "by_utterances", "by_files")
    def words(
        self, participants=None, exclude=None, by_utterances=False, by_files=False
    ) -> Union[List[str], List[List[str]], List[List[List[str]]]]:
        """Return the words.

        Parameters
        ----------

        Returns
        -------
        List[List[List[str]]] if both ``by_utterances`` and ``by_files`` are ``True``
        List[List[str]] if ``by_utterances`` is ``True`` and ``by_files`` is ``False``
        List[List[str]] if ``by_utterances`` is ``False`` and ``by_files`` is ``True``
        List[str] if both ``by_utterances`` and ``by_files`` are ``False``
        """
        tokens = self.tokens(
            participants=participants,
            exclude=exclude,
            by_utterances=True,
            by_files=True,
        )
        result = [
            [[t.word for t in ts if t.word != _CLITIC] for ts in tss] for tss in tokens
        ]
        return self._get_result_by_utterances_by_files(result, by_utterances, by_files)

    def _filter_utterances_by_participants(
        self, participants, exclude
    ) -> List[List[Utterance]]:
        if participants and exclude:
            raise TypeError(
                "participants and exclude cannot be specified at the same time: "
                f"{participants}, {exclude}"
            )

        if participants is None:
            participants: List[Set] = self.participants(by_files=True)
        elif type(participants) == str:
            participants: List[Set] = [{participants} for _ in range(self.n_files())]
        elif hasattr(participants, "__iter__"):
            participants: List[Set] = [set(participants) for _ in range(self.n_files())]
        else:
            raise ValueError(
                "participants must be one of {None, a string, an iterable of strings}: "
                f"{participants}"
            )

        if exclude is None:
            pass
        elif type(exclude) == str:
            participants: List[Set] = [p - {exclude} for p in participants]
        elif hasattr(exclude, "__iter__"):
            participants: List[Set] = [p - set(exclude) for p in participants]
        else:
            raise ValueError(
                "exclude must be one of {None, a string, an iterable of strings}: "
                f"{exclude}"
            )

        return [
            [u for u in us if u.participant in ps]
            for us, ps in zip([f.utterances for f in self._files], participants)
        ]

    def headers(self) -> List[Dict]:
        """Return the headers.

        Returns
        -------
        List[Dict]
        """
        return [f.header for f in self._files]

    def file_paths(self) -> List[str]:
        """Return the file paths.

        If the data comes from in-memory strings, then the "file paths" are
        arbitrary UUID random strings.

        Returns
        -------
        List[str]
        """
        return [f.file_path for f in self._files]

    def n_files(self) -> int:
        """Return the number of files."""
        return len(self._files)

    @_params_in_docstring("by_files")
    def participants(self, by_files=False) -> Union[Set[str], List[Set[str]]]:
        """Return the participants (e.g., CHI, MOT).

        Parameters
        ----------

        Returns
        -------
        Set[str] if ``by_files`` is ``False``, otherwise List[Set[str]]
        """
        result_by_files = [{u.participant for u in f.utterances} for f in self._files]
        if by_files:
            return result_by_files
        else:
            return self._flatten(set, result_by_files)

    @_params_in_docstring("by_files")
    def languages(self, by_files=False) -> Union[Set[str], List[List[str]]]:
        """Return the languages in the data.

        Parameters
        ----------

        Returns
        -------
        Set[str] if ``by_files`` is ``False``, otherwise List[List[str]]
            When ``by_files`` is ``True``, the ordering of languages given by the list
            indicates language dominance. Such ordering would not make sense when
            ``by_files`` is ``False``, in which case the returned object is a set
            instead of a list.
        """
        result_by_files = [f.header.get("Languages", []) for f in self._files]
        if by_files:
            return result_by_files
        else:
            return set(self._flatten(list, result_by_files))

    @_params_in_docstring("by_files")
    def dates_of_recording(
        self, by_files=False
    ) -> Union[Set[datetime.date], List[Set[datetime.date]]]:
        """Return the dates of recording.

        Parameters
        ----------

        Returns
        -------
        Set[datetime.date] if ``by_files`` is ``False``,
        otherwise List[Set[datetime.date]]]
        """
        result_by_files = [f.header["Date"] for f in self._files]
        if by_files:
            return result_by_files
        else:
            return self._flatten(set, result_by_files)

    def ages(
        self, participant="CHI", months=False
    ) -> Union[List[Tuple[int, int, int]], List[float]]:
        """Return the ages of the given participant in the data.

        Parameters
        ----------
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.
        months : bool, optional
            If ``False`` (the default), age is represented as a tuple of
            (years, months, days), e.g., "1;06.00" in CHAT becomes ``(1, 6, 0)``.
            If ``True``, age is a float for the number of months,
            e.g., "1;06.00" in CHAT becomes ``18.0`` for 18 months.

        Returns
        -------
        List[Tuple[int, int, int]] if ``months`` is ``False``, otherwise List[float]
        """
        result_by_files = []
        for f in self._files:
            try:
                age = f.header["Participants"][participant]["age"]

                year_str, _, month_day = age.partition(";")
                month_str, _, day_str = month_day.partition(".")

                year_int = int(year_str) if year_str.isdigit() else 0
                month_int = int(month_str) if month_str.isdigit() else 0
                day_int = int(day_str) if day_str.isdigit() else 0

                if months:
                    result = year_int * 12 + month_int + day_int / 30
                else:
                    result = (year_int, month_int, day_int)
            except (KeyError, IndexError, ValueError):
                result = None
            result_by_files.append(result)
        return result_by_files

    @_params_in_docstring("participants", "exclude", "by_files")
    def tagged_sents(
        self, participants=None, exclude=None, by_files=False
    ) -> Union[List[List[Token]], List[List[List[Token]]]]:
        """Return the tagged sents.

        .. deprecated:: 0.13.0
            Please use :func:`~pylangacq.Reader.tokens` with ``by_utterances=True``
            instead.

        Parameters
        ----------

        Returns
        -------
        List[List[Token]] if ``by_files`` is ``False``,
        otherwise List[List[List[Token]]]
        """
        _deprecate_warning(
            "tagged_sents",
            "0.13.0",
            "the `.tokens()` method with by_utterances=True",
        )
        utterances = self._filter_utterances_by_participants(participants, exclude)
        result_by_files = [[u.tokens for u in us] for us in utterances]
        if by_files:
            return result_by_files
        else:
            return self._flatten(list, result_by_files)

    @_params_in_docstring("participants", "exclude", "by_files")
    def tagged_words(
        self, participants=None, exclude=None, by_files=False
    ) -> Union[List[Token], List[List[Token]]]:
        """Return the tagged words.

        .. deprecated:: 0.13.0
            Please use :func:`~pylangacq.Reader.tokens` with ``by_utterances=False``
            instead.

        Parameters
        ----------

        Returns
        -------
        List[Token] if ``by_files`` is ``False``, otherwise List[List[Token]]
        """
        _deprecate_warning(
            "tagged_words", "0.13.0", "the `.tokens()` method with by_utterances=False"
        )
        utterances = self._filter_utterances_by_participants(participants, exclude)
        result_by_files = [[word for u in us for word in u.tokens] for us in utterances]
        if by_files:
            return result_by_files
        else:
            return self._flatten(list, result_by_files)

    @_params_in_docstring("participants", "exclude", "by_files")
    def sents(
        self, participants=None, exclude=None, by_files=False
    ) -> Union[List[List[str]], List[List[List[str]]]]:
        """Return the sents.

        .. deprecated:: 0.13.0
            Please use :func:`~pylangacq.Reader.words` with ``by_utterances=True``
            instead.

        Parameters
        ----------

        Returns
        -------
        List[List[str]] if ``by_files`` is ``False``, otherwise List[List[List[str]]]
        """
        _deprecate_warning(
            "words", "0.13.0", "the `.words()` method with by_utterances=True"
        )
        utterances = self._filter_utterances_by_participants(participants, exclude)
        result_by_files = [
            [[t.word for t in u.tokens] for u in us] for us in utterances
        ]
        if by_files:
            return result_by_files
        else:
            return self._flatten(list, result_by_files)

    def mlum(self, participant="CHI") -> List[float]:
        """Return the mean lengths of utterance by morphemes.

        Parameters
        ----------
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.

        Returns
        -------
        List[float]
        """
        return _get_mlum(
            self.tokens(participants=participant, by_utterances=True, by_files=True)
        )

    def mlu(self, participant="CHI") -> List[float]:
        """Return the mean lengths of utterance (MLU).

        This method is equivalent to :func:`~pylangacq.chat.Reader.mlum`.

        Parameters
        ----------
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.

        Returns
        -------
        List[float]
        """
        return self.mlum(participant=participant)

    def mluw(self, participant="CHI") -> List[float]:
        """Return the mean lengths of utterance by words.

        Parameters
        ----------
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.

        Returns
        -------
        List[float]
        """
        return _get_mluw(
            self.words(participants=participant, by_utterances=True, by_files=True)
        )

    def ttr(self, keep_case=True, participant="CHI") -> List[float]:
        """Return the type-token ratios.

        Parameters
        ----------
        keep_case : bool, optional
            If ``True``, case distinctions are kept, e.g.,
            word tokens like "the" and "The" are treated as distinct.
            If ``False`` (the default), all word tokens are forced to be in lowercase
            as a preprocessing step.
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.

        Returns
        -------
        List[float]
        """
        return _get_ttr(
            self.word_frequencies(
                keep_case=keep_case, participants=participant, by_files=True
            )
        )

    def ipsyn(self, participant="CHI") -> List[int]:
        """Return the indexes of productive syntax (IPSyn).

        Parameters
        ----------
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.

        Returns
        -------
        List[float]
        """
        return _get_ipsyn(
            self.tokens(participants=participant, by_utterances=True, by_files=True)
        )

    @_params_in_docstring("keep_case", "participants", "exclude", "by_files")
    def word_ngrams(
        self, n, keep_case=True, participants=None, exclude=None, by_files=False
    ) -> Union[collections.Counter, List[collections.Counter]]:
        """Return word ngrams.

        Parameters
        ----------

        Returns
        -------
        collections.Counter if ``by_files`` is ``False``,
        otherwise List[collections.Counter]
        """

        err_msg = f"n must be a positive integer: {n}"
        if type(n) != int:
            raise TypeError(err_msg)
        elif n < 1:
            raise ValueError(err_msg)

        result_by_files = []

        for sents_in_file in self.words(
            participants=participants,
            exclude=exclude,
            by_utterances=True,
            by_files=True,
        ):
            result_for_file = collections.Counter()
            for sent in sents_in_file:
                if len(sent) < n:
                    continue
                if not keep_case:
                    sent = [w.lower() for w in sent]
                ngrams = zip(*[sent[i:] for i in range(n)])
                result_for_file.update(ngrams)
            result_by_files.append(result_for_file)

        if by_files:
            return result_by_files
        else:
            return self._flatten(collections.Counter, result_by_files)

    @_params_in_docstring("keep_case", "participants", "exclude", "by_files")
    def word_frequencies(
        self, keep_case=True, participants=None, exclude=None, by_files=False
    ) -> Union[collections.Counter, List[collections.Counter]]:
        """Return word frequencies.

        Parameters
        ----------

        Returns
        -------
        collections.Counter if ``by_files`` is ``False``,
        otherwise List[collections.Counter]
        """
        result_by_files = self.word_ngrams(
            1,
            keep_case=keep_case,
            participants=participants,
            exclude=exclude,
            by_files=True,
        )
        result_by_files = [
            collections.Counter({k[0]: v for k, v in r.items()})
            for r in result_by_files
        ]
        if by_files:
            return result_by_files
        else:
            return self._flatten(collections.Counter, result_by_files)

    @classmethod
    def from_strs(cls, strs: List[str], ids: List[str] = None) -> "Reader":
        """Instantiate a reader from in-memory CHAT data strings.

        Parameters
        ----------
        strs : List[str]
            List of CHAT data strings. The ordering of the strings determines
            that of the parsed CHAT data in the resulting reader.
        ids : List[str], optional
            List of identifiers. If not provided, UUID random strings are used.
            When file paths are referred to in other parts of this package, they
            mean these identifiers if you have instantiated the reader by this method.

        Returns
        -------
        Reader
        """
        strs = list(strs)
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(strs))]
        else:
            ids = list(ids)
        if len(strs) != len(ids):
            raise ValueError(
                f"strs and ids must have the same size: {len(strs)} and {len(ids)}"
            )
        reader = cls()
        reader._parse_chat_strs(strs, ids)
        return reader

    @classmethod
    @_params_in_docstring("match", "exclude", "encoding")
    def from_files(
        cls,
        paths: List[str],
        match: str = None,
        exclude: str = None,
        encoding: str = _ENCODING,
    ) -> "Reader":
        """Instantiate a reader from local CHAT data files.

        Parameters
        ----------
        paths : List[str]
            List of local file paths of the CHAT data. The ordering of the paths
            determines that of the parsed CHAT data in the resulting reader.

        Returns
        -------
        Reader
        """

        # Inner function with file closing and closure to wrap in the given encoding
        def _open_file(path: str) -> str:
            with open(path, encoding=encoding) as f:
                return f.read()

        paths = list(paths)

        if match:
            regex = re.compile(match)
            paths = [p for p in paths if regex.search(p)]

        if exclude:
            regex = re.compile(exclude)
            paths = [p for p in paths if not regex.search(p)]

        with cf.ThreadPoolExecutor() as executor:
            strs = list(executor.map(_open_file, paths))

        return cls.from_strs(strs, paths)

    @classmethod
    @_params_in_docstring("match", "exclude", "extension", "encoding")
    def from_dir(
        cls,
        path: str,
        match: str = None,
        exclude: str = None,
        extension: str = _CHAT_EXTENSION,
        encoding: str = _ENCODING,
    ) -> "Reader":
        """Instantiate a reader from a local directory with CHAT data files.

        Parameters
        ----------
        path : str
            Local directory that contains CHAT data files. Files are searched for
            recursively under this directory, and those that satisfy ``match`` and
            ``extension`` are parsed and handled by the reader.

        Returns
        -------
        Reader
        """

        file_paths = []
        for dirpath, _, filenames in os.walk(path):
            if not filenames:
                continue
            for filename in filenames:
                if not filename.endswith(extension):
                    continue
                file_paths.append(os.path.join(dirpath, filename))
        return cls.from_files(
            sorted(file_paths), match=match, exclude=exclude, encoding=encoding
        )

    @classmethod
    @_params_in_docstring("match", "exclude", "extension", "allow_remote", "encoding")
    def from_zip(
        cls,
        path: str,
        match: str = None,
        exclude: str = None,
        extension: str = _CHAT_EXTENSION,
        allow_remote: bool = True,
        encoding: str = _ENCODING,
    ) -> "Reader":
        """Instantiate a reader from a local or remote ZIP file.

        Parameters
        ----------
        path : str
            Either a local file path or a URL (one that begins with ``"https://"``
            or ``"http://"``) for a ZIP file containing CHAT data files.
            For instance, you can provide either a local path to a ZIP file downloaded
            from CHILDES, or simply a URL such as
            ``"https://childes.talkbank.org/data/Eng-NA/Brown.zip"``.

        Returns
        -------
        Reader
        """
        with contextlib.ExitStack() as stack:
            temp_dir = stack.enter_context(tempfile.TemporaryDirectory())
            is_url = path.startswith("https://") or path.startswith("http://")

            if allow_remote and is_url:
                zip_path = os.path.join(temp_dir, os.path.basename(path))
                _download_file(path, zip_path)
            else:
                zip_path = path

            zfile = stack.enter_context(zipfile.ZipFile(zip_path))
            zfile.extractall(temp_dir)

            if allow_remote and is_url:
                os.remove(zip_path)

            reader = cls.from_dir(
                temp_dir,
                match=match,
                exclude=exclude,
                extension=extension,
                encoding=encoding,
            )

        # Unzipped files from `.from_zip` have the unwieldy temp dir in the file path.
        for f in reader._files:
            f.file_path = f.file_path.replace(temp_dir, "").lstrip(os.sep)

        return reader

    def _parse_chat_str(self, chat_str, file_path) -> _File:
        lines = self._get_lines(chat_str)
        header = self._get_header(lines)
        all_tiers = self._get_all_tiers(lines)
        utterances = self._get_utterances(all_tiers)
        return _File(file_path, header, utterances)

    def _get_participant_code(self, tier_markers: Iterable[str]) -> Union[str, None]:
        for tier_marker in tier_markers:
            if not tier_marker.startswith("%"):
                return tier_marker
        return None

    def _get_utterances(self, all_tiers: Iterable[Dict[str, str]]) -> List[Utterance]:
        result_list = []

        for tiermarker_to_line in all_tiers:
            participant_code = self._get_participant_code(tiermarker_to_line.keys())

            if participant_code is None:
                continue

            # get the plain words from utterance tier
            utterance_line = _clean_utterance(tiermarker_to_line[participant_code])
            forms = utterance_line.split()

            # %mor tier
            clitic_indices = []  # indices at the word items
            clitic_count = 0

            mor_items = []
            if "%mor" in tiermarker_to_line:
                mor_split = tiermarker_to_line["%mor"].split()

                for j, item in enumerate(mor_split):
                    tilde_count = item.count("~")

                    if tilde_count:
                        item_split = item.split("~")

                        for k in range(tilde_count):
                            clitic_indices.append(clitic_count + j + k + 1)
                            clitic_count += 1

                            mor_items.append(item_split[k])

                        mor_items.append(item_split[-1])
                    else:
                        mor_items.append(item)

            if mor_items and ((len(forms) + clitic_count) != len(mor_items)):
                raise ValueError(
                    "cannot align the utterance and %mor tiers:\n"
                    f"Tiers --\n{tiermarker_to_line}\n"
                    f"Cleaned-up utterance --\n{utterance_line}"
                )

            # %gra tier
            gra_items = (
                tiermarker_to_line["%gra"].split()
                if "%gra" in tiermarker_to_line
                else []
            )

            if mor_items and gra_items and (len(mor_items) != len(gra_items)):
                raise ValueError(
                    f"cannot align the %mor and %gra tiers:\n{tiermarker_to_line}"
                )

            # utterance tier
            if mor_items and clitic_count:
                word_iterator = iter(forms)
                utterance_items = [""] * len(mor_items)

                for j in range(len(mor_items)):
                    if j in clitic_indices:
                        utterance_items[j] = _CLITIC
                    else:
                        utterance_items[j] = next(word_iterator)
            else:
                utterance_items = forms

            # determine what to yield (and how) to create the generator
            if not mor_items:
                mor_items = [None] * len(utterance_items)
            if not gra_items:
                gra_items = [None] * len(utterance_items)

            sent: List[Token] = []

            for word, mor, gra in zip(utterance_items, mor_items, gra_items):
                try:
                    pos, _, mor = mor.partition("|")
                except AttributeError:
                    pos, mor = None, None

                output_word = Token(
                    _clean_word(word),
                    self._preprocess_pos(pos),
                    mor,
                    self._get_gra(gra),
                )
                sent.append(self._preprocess_token(output_word))

            time_marks = self._get_time_marks(tiermarker_to_line[participant_code])
            u = Utterance(participant_code, sent, time_marks, tiermarker_to_line)
            result_list.append(self._preprocess_utterance(u))

        return result_list

    @staticmethod
    def _preprocess_token(t: Token):
        """Override this method in a child class for custom behavior."""
        return t

    @staticmethod
    def _preprocess_utterance(u: Utterance):
        """Override this method in a child class for custom behavior."""
        return u

    @staticmethod
    def _preprocess_pos(pos: str) -> str:
        """If POS tag preprocessing is needed, create a child class of Reader and
        override this method."""
        return pos

    @staticmethod
    def _get_time_marks(line: str) -> Union[Tuple[int, int], None]:
        match = _TIMER_MARKS_REGEX.search(line)
        if match:
            time_marks = match.groups()
            return int(time_marks[0]), int(time_marks[1])
        else:
            return None

    @staticmethod
    def _get_gra(raw_gra: Optional[str]) -> Union[Gra, None]:
        if raw_gra is None:
            return None
        try:
            dep, head, rel = raw_gra.strip().split("|", 2)
            dep = int(dep)
            head = int(head)
            return Gra(dep, head, rel)
        except (ValueError, TypeError):
            return None

    def _get_all_tiers(self, lines: List[str]) -> Iterable[Dict[str, str]]:
        index_to_tiers: Dict[int, Dict[str, str]] = {}
        index_ = -1  # utterance index (1st utterance is index 0)
        utterance = None

        for line in lines:
            if line.startswith("@"):
                continue

            line_split = line.split()

            if line.startswith("*"):
                index_ += 1
                participant_code = line_split[0].lstrip("*").rstrip(":")
                utterance = " ".join(line_split[1:])
                index_to_tiers[index_] = {participant_code: utterance}

            elif utterance and line.startswith("%"):
                tier_marker = line_split[0].rstrip(":")
                index_to_tiers[index_][tier_marker] = " ".join(line_split[1:])

        return index_to_tiers.values()

    def _get_header(self, lines: List[str]) -> Dict:
        headname_to_entry = {"Date": set(), "Participants": {}}

        for line in lines:

            if line.startswith("@Begin") or line.startswith("@End"):
                continue

            if not line.startswith("@"):
                continue

            # find head, e.g., "Languages", "Participants", "ID" etc
            head, _, line = line.partition("\t")
            line = line.strip()
            head = head.lstrip("@")  # remove beginning "@"
            head = head.rstrip(":")  # remove ending ":", if any

            if head == "Participants":

                participants = line.split(",")

                for participant in participants:
                    participant = participant.strip()
                    code, _, participant_label = participant.partition(" ")
                    (
                        participant_name,
                        _,
                        participant_role,
                    ) = participant_label.partition(" ")
                    # code = participant code, e.g. CHI, MOT
                    headname_to_entry["Participants"][code] = {"name": participant_name}

            elif head == "ID":
                participant_info = line.split("|")[:-1]
                # final empty str removed

                code = participant_info[2]
                # participant_info contains these in order:
                #   language, corpus, code, age, sex, group, SES, role,
                #   education, custom

                del participant_info[2]  # remove code info (3rd in list)
                participant_info_heads = [
                    "language",
                    "corpus",
                    "age",
                    "sex",
                    "group",
                    "ses",
                    "role",
                    "education",
                    "custom",
                ]
                head_to_info = dict(zip(participant_info_heads, participant_info))

                headname_to_entry["Participants"][code].update(head_to_info)

            elif head == "Date":
                try:
                    date = self._header_line_to_date(line.strip())
                except (TypeError, ValueError, ParserError):
                    continue
                headname_to_entry["Date"].add(date)

            elif head.startswith("Birth of"):
                # e.g., header is 'Birth of CHI', participant is 'CHI'
                _, _, participant = head.split()
                try:
                    date = self._header_line_to_date(line.strip())
                except (TypeError, ValueError, ParserError):
                    continue
                if participant not in headname_to_entry["Participants"]:
                    headname_to_entry["Participants"][participant] = {}
                headname_to_entry["Participants"][participant]["dob"] = date

            elif head == "Languages":
                languages = []  # not set; ordering indicates language dominance
                for language in line.strip().split(","):
                    language = language.strip()
                    if language:
                        languages.append(language)
                headname_to_entry["Languages"] = languages

            else:
                headname_to_entry[head] = line

        return headname_to_entry

    @staticmethod
    def _header_line_to_date(line: str) -> datetime.date:
        return parse_date(line).date()

    @staticmethod
    def _get_lines(raw_str: str) -> List[str]:
        lines: List[str] = []

        previous_line = ""

        for line in raw_str.splitlines():
            previous_line = previous_line.strip()
            current_line = line.rstrip()  # don't remove leading \t

            if not current_line:
                continue

            if current_line.startswith("%xpho:") or current_line.startswith("%xmod:"):
                current_line = current_line.replace("%x", "%", 1)

            if previous_line and current_line.startswith("\t"):
                previous_line = f"{previous_line} {current_line.strip()}"
            elif previous_line:
                lines.append(previous_line)
                previous_line = current_line
            else:  # when it's the very first line
                previous_line = current_line

        lines.append(previous_line)  # don't forget the very last line!

        return lines


@_params_in_docstring("match", "exclude", "encoding", "cls", class_method=False)
def read_chat(
    path: str,
    match: str = None,
    exclude: str = None,
    encoding: str = _ENCODING,
    cls: type = Reader,
) -> Reader:
    """Create a reader of CHAT data.

    Parameters
    ----------
    path : str
        A path that points to one of the following:

        - ZIP file. Either a local file path or a URL (one that begins with
          ``"https://"`` or ``"http://"``).
          Example of a URL: ``"https://childes.talkbank.org/data/Eng-NA/Brown.zip"``
        - A local directory, for files under this directory recursively.
        - A single CHAT file.

    Returns
    -------
    :class:`~pylangacq.chat.Reader`
    """
    if cls != Reader and not issubclass(cls, Reader):
        raise TypeError(f"Only a Reader class or its child class is allowed: {cls}")

    # Just in case the user provides a CHILDES web link like
    # https://childes.talkbank.org/access/Eng-NA/Brown.html
    # instead of https://childes.talkbank.org/data/Eng-NA/Brown.zip.
    # The "childes" subdomain could sometimes be "phonbank" (and something else?).
    # This hack is just for convenience.
    # Not sure if we should encourage using the .html link...
    if re.search(r"https://\S+\.talkbank\.org/access/\S+\.html", path):
        path = path.replace("/access/", "/data/")
        path = path.replace(".html", ".zip")

    path_lower = path.lower()
    if path_lower.endswith(".zip"):
        return cls.from_zip(path, match=match, exclude=exclude, encoding=encoding)
    elif os.path.isdir(path):
        return cls.from_dir(path, match=match, exclude=exclude, encoding=encoding)
    elif path_lower.endswith(_CHAT_EXTENSION):
        return cls.from_files([path], match=match, exclude=exclude, encoding=encoding)
    else:
        raise ValueError(
            "path is not one of the accepted choices of "
            f"{{zip file, local directory, `.cha` file}}: {path}"
        )


def _clean_utterance(utterance, phon=False):
    """Filter away the CHAT-style annotations in ``utterance``.

    Parameters
    ----------
    utterance : str
        The utterance as a str
    phon : bool, optional
        whether we are handling PhonBank data; defaults to ``False``.
        If ``True``, words like "xxx" and "yyy" won't be removed.

    Returns
    -------
    str
    """
    # Function tested with the following CHILDES datasets:
    # 1) Brent, Brown, HSLLD, Kuczaj, MacWhinney, Valian in Eng-NA-MOR
    # 2) YipMatthews in Biling
    # 3) LeeWongLeung in EastAsian/Cantonese
    # 4) CromptonPater, Goad, Inkelas, and Providence in PhonBank English

    # *** At the end of each step, apply remove_extra_spaces(). ***

    # Step 1: Remove unwanted scope elements (only the very certain cases)
    # [= whatever] for explanations
    # [x how_many_times] for collapses
    # [+ whatever] for actions etc
    # [* whatever] for error coding
    # [=? whatever] for uncertain transcriptions
    # [=! whatever] for actions etc
    # [% whatever] for random noises?
    # [- language_name] for using a non-dominant language
    # [^ whatever] for complex local events
    # whatever for audio/video time stamps? the  character is 0x15
    # [<] and [>] for overlapping, including [<1], [>2] etc with numbers
    # (2.), (3.5) etc for pauses
    # [%act: whatever] for actions etc

    # [?] for best guess
    # ‹ and › used in conjunction with [?]
    # [!] for stressing

    # "[*] [/" replaced by "[/"
    # "] [*]" replaced by "]"

    # print('utterance:', utterance, type(utterance))

    utterance = re.sub(r"\[= [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[x \d+?\]", "", utterance)
    utterance = re.sub(r"\[\+ [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[\* [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[=\? [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[=! [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[% [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[- [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[\^ [^\[]+?\]", "", utterance)
    utterance = re.sub(r"[^]+?", "", utterance)
    utterance = re.sub(r"\[<\d?\]", "", utterance)
    utterance = re.sub(r"\[>\d?\]", "", utterance)
    utterance = re.sub(r"\(\d+?\.?\d*?\)", "", utterance)
    utterance = re.sub(r"\[%act: [^\[]+?\]", "", utterance)

    utterance = re.sub(r"\[\?\]", "", utterance)
    utterance = re.sub(r"\[\!\]", "", utterance)
    utterance = re.sub(r"‹", "", utterance)
    utterance = re.sub(r"›", "", utterance)

    utterance = re.sub(r"\[\*\] \[/", "[/", utterance)
    utterance = re.sub(r"\] \[\*\]", "]", utterance)

    utterance = _remove_extra_spaces(utterance)
    # print('step 1:', utterance)

    # Step 2: Pad elements with spaces to avoid human transcription errors
    # If utterance has these delimiters: [ ]
    # then pad them with extra spaces to avoid errors in transcriptions
    # like "movement[?]" (--> "movement [?]")
    #
    # If utterance has:
    #     < > (left and right angle brackets), excluding "+<" (lazy overlap)
    #     “ (beginning quote)
    #     ” (ending quote)
    #     , (comma)
    #     ? (question mark)
    #     . (period) <-- commented out at the moment
    #     (.) (short pause)
    # then pad them with extra spaces.

    utterance = re.sub(r"<", " <", utterance)
    utterance = re.sub(r"\+ <", "+<", utterance)
    utterance = re.sub(r">", "> ", utterance)
    utterance = re.sub(r"\[", " [", utterance)
    utterance = re.sub(r"\]", "] ", utterance)
    utterance = re.sub(r"“", " “ ", utterance)
    utterance = re.sub(r"”", " ” ", utterance)
    utterance = re.sub(r",", " , ", utterance)  # works together with next line
    utterance = re.sub(r"\+ ,", "+,", utterance)
    utterance = re.sub(r"[^\[\./!]\?", " ? ", utterance)
    # utterance = re.sub('[^\(\[\.\+]\.', ' . ', utterance)
    utterance = re.sub(r"\(\.\)", " (.) ", utterance)
    utterance = _remove_extra_spaces(utterance)
    # print('step 2:', utterance)

    # Step 3:
    # Handle [/], [//], [///], [/?] for repetitions/reformulation
    #        [: xx] or [:: xx] for errors
    #
    # Discard "xx [/]", "<xx yy> [/]", "xx [//]", "<xx yy> [//]".
    # For "zz [: xx]" or "<yy zz> [:: xx]", keep "xx" and discard the rest.
    #
    # Strategies:
    # 1. Get all matching index pairs for angle brackets < and >.
    # 2. Delete the unwanted material inside and including these brackets
    #    plus their signaling annotations (= "[:", "[::", "[/]", "[//]").
    # 3. Delete the unwanted words on the left of the signaling annotations.

    angle_brackets_l2r_pairs = {}  # left-to-right
    for index_ in _find_indices(utterance, "<"):
        counter = 1
        for i in range(index_ + 1, len(utterance)):
            if utterance[i] == "<":
                counter += 1
            elif utterance[i] == ">":
                counter -= 1

            if counter == 0:
                angle_brackets_l2r_pairs[index_] = i
                break
    angle_brackets_r2l_pairs = {v: k for k, v in angle_brackets_l2r_pairs.items()}

    index_pairs = []  # characters bounded by index pairs to be removed

    # remove ' [///]'
    triple_slash_right_indices = _find_indices(utterance, r"> \[///\]")
    index_pairs += [(begin + 1, begin + 6) for begin in triple_slash_right_indices]

    # remove ' [//]'
    double_overlap_right_indices = _find_indices(utterance, r"> \[//\]")
    index_pairs += [(begin + 1, begin + 5) for begin in double_overlap_right_indices]

    # remove ' [/]'
    single_overlap_right_indices = _find_indices(utterance, r"> \[/\]")
    index_pairs += [(begin + 1, begin + 4) for begin in single_overlap_right_indices]

    # remove ' [/?]'
    slash_question_indices = _find_indices(utterance, r"> \[/\?\]")
    index_pairs += [(begin + 1, begin + 4) for begin in slash_question_indices]

    # remove ' [/-]'
    slash_dash_indices = _find_indices(utterance, r"> \[/\-\]")
    index_pairs += [(begin + 1, begin + 4) for begin in slash_dash_indices]

    # remove ' [::'
    double_error_right_indices = _find_indices(utterance, r"> \[::")
    index_pairs += [(begin + 1, begin + 4) for begin in double_error_right_indices]

    # remove ' [:'
    single_error_right_indices = _find_indices(utterance, r"> \[: ")
    index_pairs += [(begin + 1, begin + 3) for begin in single_error_right_indices]

    right_indices = (
        double_overlap_right_indices
        + single_overlap_right_indices
        + double_error_right_indices
        + single_error_right_indices
        + triple_slash_right_indices
        + slash_question_indices
        + slash_dash_indices
    )

    index_pairs = index_pairs + [
        (angle_brackets_r2l_pairs[right], right) for right in sorted(right_indices)
    ]
    indices_to_ignore = set()
    for left, right in index_pairs:
        for i in range(left, right + 1):
            indices_to_ignore.add(i)

    new_utterance = ""
    for i in range(len(utterance)):
        if i not in indices_to_ignore:
            new_utterance += utterance[i]
    utterance = new_utterance

    utterance = re.sub(r"\S+? \[/\]", "", utterance)
    utterance = re.sub(r"\S+? \[//\]", "", utterance)
    utterance = re.sub(r"\S+? \[///\]", "", utterance)
    utterance = re.sub(r"\S+? \[/\?\]", "", utterance)
    utterance = re.sub(r"\S+? \[/\-\]", "", utterance)

    utterance = re.sub(r"\S+? \[::", "", utterance)
    utterance = re.sub(r"\S+? \[:", "", utterance)

    utterance = _remove_extra_spaces(utterance)
    # print('step 3:', utterance)

    # Step 4: Remove unwanted symbols
    utterance = re.sub(r"“", "", utterance)
    utterance = re.sub(r"”", "", utterance)

    utterance = _remove_extra_spaces(utterance)

    # Step 5: Split utterance by spaces and determine whether to keep items.

    escape_prefixes = {
        "[?",
        "[/",
        "[<",
        "[>",
        "[:",
        "[!",
        "[*",
        '+"',
        "+,",
        "<&",
    }
    escape_words = {"0", "++", "+<", "+^", "(.)", "(..)", "(...)", ":", ";"}
    keep_prefixes = {'+"/', "+,/", '+".'}

    if not phon:
        escape_words.update({"xxx", "yyy", "www", "xxx:", "yyy:"})
        escape_prefixes.update({"&"})
    else:
        escape_words.update({","})
        escape_prefixes.update({"0"})

    words = utterance.split()
    new_words = []

    for word in words:
        word = re.sub(r"\A<", "", word)  # remove beginning <
        word = re.sub(r">\Z", "", word)  # remove final >
        word = re.sub(r"\]\Z", "", word)  # remove final ]

        not_an_escape_word = word not in escape_words
        no_escape_prefix = not any(word.startswith(e) for e in escape_prefixes)
        has_keep_prefix = any(word.startswith(k) for k in keep_prefixes)

        if (not_an_escape_word and no_escape_prefix) or has_keep_prefix:
            new_words.append(word)

    # print('step 5:', remove_extra_spaces(' '.join(new_words)))

    return _remove_extra_spaces(" ".join(new_words))


def _clean_word(word):
    """Clean the word.

    Parameters
    ----------
    word : str

    Returns
    -------
    str
    """
    new_word = (
        word.replace("(", "")
        .replace(")", "")
        .replace(":", "")
        .replace(";", "")
        .replace("+", "")
    )

    if "@" in new_word:
        new_word = new_word[: new_word.index("@")]

    if new_word.startswith("&"):
        new_word = new_word[1:]

    return new_word


def _remove_extra_spaces(inputstr):
    """Remove extra spaces in *inputstr* so that there are only single spaces.

    Parameters
    ----------
    inputstr : str

    Returns
    -------
    str
    """
    while "  " in inputstr:
        inputstr = inputstr.replace("  ", " ")
    return inputstr.strip()


def _find_indices(longstr, substring):
    """Find all indices of non-overlapping ``substring`` in ``longstr``.

    Parameters
    ----------
    longstr : str
    substring : str

    Returns
    -------
    list of int
        List of indices of the long string for where substring occurs
    """
    return [m.start() for m in re.finditer(substring, longstr)]


class _HTTPSession(requests.Session):
    def __init__(
        self, max_retries: int = 10, backoff_factor: float = 0.1, timeout: int = 60
    ):
        super().__init__()
        retry = Retry(total=max_retries, backoff_factor=backoff_factor)
        adapter = HTTPAdapter(max_retries=retry)
        self.mount("http://", adapter)
        self.mount("https://", adapter)
        self.timeout = timeout

    def request(self, *args, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return super(_HTTPSession, self).request(*args, **kwargs)


def _download_file(url, path):
    with contextlib.ExitStack() as stack:
        f = stack.enter_context(open(path, "wb"))
        r = stack.enter_context(_HTTPSession().get(url, stream=True))
        shutil.copyfileobj(r.raw, f)
