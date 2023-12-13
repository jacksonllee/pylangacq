"""Interfacing with CHAT data files."""

import collections
import concurrent.futures as cf
import dataclasses
import datetime
import functools
import itertools
import json
import os
import re
import shutil
import tempfile
import uuid
import warnings
import zipfile
from typing import Dict, Generator, Iterable, List, Optional, Set, Tuple, Union

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dateutil.parser import parse as parse_date
from dateutil.parser import ParserError
from tabulate import tabulate

import pylangacq
from .measures import _get_ipsyn, _get_mlum, _get_mluw, _get_ttr
from .objects import (
    Gra,
    Token,
    Utterance,
    _sort_keys,
    _CLITICS,
    _PRECLITIC,
    _POSTCLITIC,
)
from ._clean_utterance import _clean_utterance


_ENCODING = "utf-8"

_CHAT_EXTENSION = ".cha"

_TIMER_MARKS_REGEX = re.compile(r"\x15-?(\d+)_(\d+)-?\x15")

_CACHED_DATA_DIR = os.path.join(os.path.expanduser("~"), ".pylangacq")
_CACHED_DATA_JSON_PATH = os.path.join(_CACHED_DATA_DIR, "cached_data.json")

_CHAT_LINE_INDICATORS = frozenset({"@", "*", "%"})

_HEADER_REGEX = re.compile(r"\A@([^@:]+)(:\s+(\S[\S\s]+))?\Z")

_CLITIC_REGEX = re.compile(r"((.+)\$)?([^$~]+)(~(.+))?")


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
            the unzipped Brown data from CHILDES has a directory structure of
            ``Brown/Eve/xxx.cha`` for Eve's data.
            If this parameter is not specified or ``None`` is passed in (the default),
            such file path filtering does not apply.
        exclude : str, optional
            If provided, the file paths that match this string (by regular expression
            matching) are excluded for reading and parsing."""

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
            Either :class:`~pylangacq.Reader` (the default),
            or a subclass from it that expects the same arguments for the methods
            :func:`~pylangacq.Reader.from_zip`, :func:`~pylangacq.Reader.from_dir`,
            and :func:`~pylangacq.Reader.from_files`.
            Pass in your own :class:`~pylangacq.Reader` subclass
            for new or modified behavior of the returned reader object."""

    if "parallel" in params:
        docstring += """
        parallel : bool, optional
            If ``True`` (the default), CHAT reading and parsing is parallelized
            for speed-up, because in most cases multiple CHAT data files and/or strings
            are being handled.
            Under certain circumstances (e.g., your application is already parallelized
            and further parallelization from within PyLangAcq might be undesirable),
            you may like to consider setting this parameter to ``False``."""

    if "use_cached" in params:
        docstring += """
        use_cached : bool, optional
            If ``True`` (the default), and if the path is a URL for a remote ZIP
            archive, then CHAT reading attempts to use the previously downloaded
            data cached on disk. This setting allows you to call
            this function with the same URL repeatedly without hitting the CHILDES /
            TalkBank server more than once for the same data.
            Pass in ``False`` to force a new download; the upstream CHILDES / TalkBank
            data is updated in minor ways from time to time, e.g., for CHAT format,
            header/metadata information, updated annotations.
            See also the helper functions: :func:`pylangacq.chat.cached_data_info`,
            :func:`pylangacq.chat.remove_cached_data`."""

    if "session" in params:
        docstring += """
        session : requests.Session, optional
            If the path is a URL for a remote ZIP archive, data downloading is
            done with reasonable settings of retries and timeout by default,
            in order to be robust against intermittent network issues.
            If necessary, pass in your own instance of :class:`requests.Session`
            to customize."""

    if not class_method:
        docstring = docstring.replace("\n        ", "\n    ")

    def real_decorator(func):
        returns_none = (
            f"Returns\n{'        ' if class_method else '    '}-------"
            not in func.__doc__
        )
        if returns_none:
            func.__doc__ += docstring
        else:
            if class_method:
                returns_header = "\n\n        Returns\n        -------"
            else:
                returns_header = "\n\n    Returns\n    -------"
            func.__doc__ = func.__doc__.replace(
                returns_header, docstring + returns_header
            )

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


class _list(list):
    def __repr__(self):
        return "\n".join(x._to_str() for x in self)

    def _repr_html_(self) -> str:
        return "\n".join(x._repr_html_() for x in self)


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

    def _parse_chat_strs(
        self, strs: List[str], file_paths: List[str], parallel: bool
    ) -> None:
        if parallel:
            with cf.ProcessPoolExecutor() as executor:
                self._files = collections.deque(
                    executor.map(self._parse_chat_str, strs, file_paths)
                )
        else:
            self._files = collections.deque(
                self._parse_chat_str(s, f) for s, f in zip(strs, file_paths)
            )

    def __len__(self):
        raise NotImplementedError(
            "__len__ of a CHAT reader is intentionally undefined. "
            "Intuitively, there are different lengths one may refer to: "
            "Number of files in this reader? Utterances? Words? Something else?"
        )

    def _get_reader_from_files(self, files: Iterable[_File]) -> "pylangacq.Reader":
        reader = self.__class__()
        reader._files = collections.deque(files)
        return reader

    def __iter__(self):
        yield from (self._get_reader_from_files([f]) for f in self._files)

    def __getitem__(self, item):
        if type(item) is int:
            return self._get_reader_from_files([self._files[item]])
        elif type(item) is slice:
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

    def __add__(self, other: "pylangacq.Reader") -> "pylangacq.Reader":
        if not issubclass(other.__class__, Reader):
            raise TypeError(f'cannot concatenate "{other.__class__}" to a reader')
        return self._get_reader_from_files(self._files + other._files)

    def _append(self, left_or_right, reader: "pylangacq.Reader") -> None:
        func = "extendleft" if left_or_right == "left" else "extend"
        if not issubclass(reader.__class__, Reader):
            raise TypeError(f"not a Reader object: {type(reader)}")
        getattr(self._files, func)(reader._files)

    def append(self, reader: "pylangacq.Reader") -> None:
        """Append data from another reader.

        New data is appended as-is with no filtering of any sort,
        even for files whose file paths duplicate those already in the current reader.

        Parameters
        ----------
        reader : Reader
            A reader from which to append data
        """
        self._append("right", reader)

    def append_left(self, reader: "pylangacq.Reader") -> None:
        """Left-append data from another reader.

        New data is appended as-is with no filtering of any sort,
        even for files whose file paths duplicate those already in the current reader.

        Parameters
        ----------
        reader : Reader
            A reader from which to left-append data
        """
        self._append("left", reader)

    def _extend(self, left_or_right, readers: "Iterable[pylangacq.Reader]") -> None:
        # Loop through each object in ``readers`` explicitly, so that we have
        # a chance to check that the object is indeed a Reader instance.
        new_files = []
        for reader in readers:
            if not issubclass(reader.__class__, Reader):
                raise TypeError(f"not a Reader object: {type(reader)}")
            new_files.extend(reader._files)
        func = "extendleft" if left_or_right == "left" else "extend"
        getattr(self._files, func)(new_files)

    def extend(self, readers: "Iterable[pylangacq.Reader]") -> None:
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

    def extend_left(self, readers: "Iterable[pylangacq.Reader]") -> None:
        """Left-extend data from other readers.

        New data is appended as-is with no filtering of any sort,
        even for files whose file paths duplicate those already in the current reader.

        Parameters
        ----------
        readers : Iterable[Reader]
            Readers from which to extend data
        """
        self._extend("left", readers)

    def _pop(self, left_or_right) -> "pylangacq.Reader":
        func = "popleft" if left_or_right == "left" else "pop"
        file_ = getattr(self._files, func)()
        return self._get_reader_from_files([file_])

    def pop(self) -> "pylangacq.Reader":
        """Drop the last data file from the reader and return it as a reader.

        Returns
        -------
        :class:`pylangacq.Reader`
        """
        return self._pop("right")

    def pop_left(self) -> "pylangacq.Reader":
        """Drop the first data file from the reader and return it as a reader.

        Returns
        -------
        :class:`pylangacq.Reader`
        """
        return self._pop("left")

    @_params_in_docstring("match", "exclude")
    def filter(self, match: str = None, exclude: str = None) -> "pylangacq.Reader":
        """Return a new reader filtered by file paths.

        Parameters
        ----------


        Returns
        -------
        :class:`pylangacq.Reader`

        Raises
        ------
        TypeError
            If neither ``match`` nor ``exclude`` is specified.
        """
        if not match and not exclude:
            raise TypeError("At least one of {match, exclude} must be specified")
        reader = self.__class__()
        file_paths = set(self._filter_file_paths(self.file_paths(), match, exclude))
        reader._files = collections.deque(
            f for f in self._files if f.file_path in file_paths
        )
        return reader

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
            [[t.word for t in ts if t.word not in _CLITICS] for ts in tss]
            for tss in tokens
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
        elif type(participants) is str:
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
        elif type(exclude) is str:
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
        result_by_files = [f.header.get("Date", set()) for f in self._files]
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

    def mlum(self, participant="CHI", exclude_switch: bool = False) -> List[float]:
        """Return the mean lengths of utterance in morphemes.

        Parameters
        ----------
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.
        exclude_switch : bool, optional
            If ``True``, exclude words with the suffix "@s" for switching to another
            language (not uncommon in code-mixing or multilingual acquisition).
            The default is ``False``.

        Returns
        -------
        List[float]
        """
        return _get_mlum(
            self.tokens(participants=participant, by_utterances=True, by_files=True),
            exclude_switch,
        )

    def mlu(self, participant="CHI", exclude_switch: bool = False) -> List[float]:
        """Return the mean lengths of utterance (MLU).

        This method is equivalent to :func:`~pylangacq.Reader.mlum`.

        Parameters
        ----------
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.
        exclude_switch : bool, optional
            If ``True``, exclude words with the suffix "@s" for switching to another
            language (not uncommon in code-mixing or multilingual acquisition).
            The default is ``False``.

        Returns
        -------
        List[float]
        """
        return self.mlum(participant=participant, exclude_switch=exclude_switch)

    def mluw(self, participant="CHI", exclude_switch: bool = False) -> List[float]:
        """Return the mean lengths of utterance in words.

        Parameters
        ----------
        participant : str, optional
            Participant of interest, which defaults to the typical use case of ``"CHI"``
            for the target child.
        exclude_switch : bool, optional
            If ``True``, exclude words with the suffix "@s" for switching to another
            language (not uncommon in code-mixing or multilingual acquisition).
            The default is ``False``.

        Returns
        -------
        List[float]
        """
        return _get_mluw(
            self.words(participants=participant, by_utterances=True, by_files=True),
            exclude_switch,
        )

    def ttr(self, keep_case=True, participant="CHI") -> List[float]:
        """Return the type-token ratios (TTR).

        Parameters
        ----------
        keep_case : bool, optional
            If ``True`` (the default), case distinctions are kept, e.g.,
            word tokens like "the" and "The" are treated as distinct.
            If ``False``, all word tokens are forced to be in lowercase
            as a preprocessing step.
            CHAT data from CHILDES intentionally does not follow the orthographic
            convention of capitalizing the first letter of a sentence in the
            transcriptions (as would have been done in many European languages),
            and so leaving keep_case as True is appropriate in most cases.
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
        if type(n) is not int:
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
    @_params_in_docstring("parallel")
    def from_strs(
        cls, strs: List[str], ids: List[str] = None, parallel: bool = True
    ) -> "pylangacq.Reader":
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
        :class:`pylangacq.Reader`
        """
        strs = list(strs)
        if ids is None:
            ids = [_get_uuid() for _ in range(len(strs))]
        else:
            ids = list(ids)
        if len(strs) != len(ids):
            raise ValueError(
                f"strs and ids must have the same size: {len(strs)} and {len(ids)}"
            )
        reader = cls()
        reader._parse_chat_strs(strs, ids, parallel)
        return reader

    @classmethod
    @_params_in_docstring("match", "exclude", "encoding", "parallel")
    def from_files(
        cls,
        paths: List[str],
        match: str = None,
        exclude: str = None,
        encoding: str = _ENCODING,
        parallel: bool = True,
    ) -> "pylangacq.Reader":
        """Instantiate a reader from local CHAT data files.

        Parameters
        ----------
        paths : List[str]
            List of local file paths of the CHAT data. The ordering of the paths
            determines that of the parsed CHAT data in the resulting reader.

        Returns
        -------
        :class:`pylangacq.Reader`
        """

        # Inner function with file closing and closure to wrap in the given encoding
        def _open_file(path: str) -> str:
            with open(path, encoding=encoding) as f:
                return f.read()

        paths = cls._filter_file_paths(paths, match, exclude)

        if parallel:
            with cf.ThreadPoolExecutor() as executor:
                strs = list(executor.map(_open_file, paths))
        else:
            strs = [_open_file(p) for p in paths]

        return cls.from_strs(strs, paths, parallel=parallel)

    @staticmethod
    def _filter_file_paths(
        paths: List[str], match: str = None, exclude: str = None
    ) -> List[str]:
        paths = list(paths)
        if match:
            regex = re.compile(match)
            paths = [p for p in paths if regex.search(p)]
        if exclude:
            regex = re.compile(exclude)
            paths = [p for p in paths if not regex.search(p)]
        return paths

    @classmethod
    @_params_in_docstring("match", "exclude", "extension", "encoding", "parallel")
    def from_dir(
        cls,
        path: str,
        match: str = None,
        exclude: str = None,
        extension: str = _CHAT_EXTENSION,
        encoding: str = _ENCODING,
        parallel: bool = True,
    ) -> "pylangacq.Reader":
        """Instantiate a reader from a local directory with CHAT data files.

        Parameters
        ----------
        path : str
            Local directory that contains CHAT data files. Files are searched for
            recursively under this directory, and those that satisfy ``match`` and
            ``extension`` are parsed and handled by the reader.

        Returns
        -------
        :class:`pylangacq.Reader`
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
            sorted(file_paths),
            match=match,
            exclude=exclude,
            encoding=encoding,
            parallel=parallel,
        )

    @classmethod
    @_params_in_docstring(
        "match",
        "exclude",
        "extension",
        "encoding",
        "parallel",
        "use_cached",
        "session",
    )
    def from_zip(
        cls,
        path: str,
        match: str = None,
        exclude: str = None,
        extension: str = _CHAT_EXTENSION,
        encoding: str = _ENCODING,
        parallel: bool = True,
        use_cached: bool = True,
        session: requests.Session = None,
    ) -> "pylangacq.Reader":
        """Instantiate a reader from a local or remote ZIP file.

        If the input data is a remote ZIP file and you expect to call this method
        with the same path multiple times, consider downloading the data to the local
        system and then reading it from there to avoid unnecessary re-downloading.
        Caching a remote ZIP file isn't implemented (yet) as the upstream CHILDES /
        TalkBank data is updated in minor ways from time to time.

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
        :class:`pylangacq.Reader`
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            is_url = path.startswith("https://") or path.startswith("http://")
            unzip_dir = cls._retrieve_unzip_dir(path) if is_url else None

            if is_url and (not use_cached or not unzip_dir):
                if unzip_dir:
                    remove_cached_data(path)
                zip_path = os.path.join(temp_dir, os.path.basename(path))
                _download_file(path, zip_path, session)
                unzip_dir = cls._create_unzip_dir(path)
            elif is_url and unzip_dir:
                zip_path = None
            else:
                zip_path = path
                unzip_dir = temp_dir

            if zip_path:
                with zipfile.ZipFile(zip_path) as zfile:
                    zfile.extractall(unzip_dir)

            reader = cls.from_dir(
                unzip_dir,
                match=match,
                exclude=exclude,
                extension=extension,
                encoding=encoding,
                parallel=parallel,
            )

        # Unzipped files from `.from_zip` have the unwieldy temp dir in the file path.
        for f in reader._files:
            f.file_path = f.file_path.replace(unzip_dir, "").lstrip(os.sep)

        return reader

    @staticmethod
    def _retrieve_unzip_dir(url: str) -> Union[str, None]:
        try:
            existing_records = json.load(open(_CACHED_DATA_JSON_PATH, encoding="utf-8"))
        except FileNotFoundError:
            return None
        subdir = existing_records.get(url, {}).get("subdir")
        if subdir is None:
            return None
        else:
            return os.path.join(_CACHED_DATA_DIR, subdir)

    @staticmethod
    def _create_unzip_dir(url: str) -> str:
        if not os.path.isdir(_CACHED_DATA_DIR):
            _initialize_cached_data_dir()

        subdir = _get_uuid()
        unzip_dir = os.path.join(_CACHED_DATA_DIR, subdir)
        os.makedirs(unzip_dir)

        new_record = {
            "subdir": subdir,
            "url": url,
            "cached_at": datetime.datetime.now().isoformat(),
        }
        existing_records = json.load(open(_CACHED_DATA_JSON_PATH, encoding="utf-8"))
        _write_cached_data_json({**existing_records, **{url: new_record}})

        return unzip_dir

    def to_strs(self, tabular: bool = True) -> Generator[str, None, None]:
        """Yield CHAT data strings.

        .. note::
            The header information may not be completely reproduced in the output
            CHAT strings. Known issues all have to do with a header field used
            multiple times in the original CHAT data.
            For ``Date``, only the first date of recording is retained in the output
            string.
            For all other multiply used header fields
            (e.g., ``Tape Location``, ``Time Duration``),
            only the last value in a given CHAT file is retained.
            Note that ``ID`` for participant information is not affected.

        Parameters
        ----------
        tabular : bool, optional
            If ``True``, adjust spacing such that the three tiers of the utterance,
            %mor, and %gra are aligned in a tabular form. Note that such alignment
            would drop annotations (e.g., pauses) on the main utterance tier.

        Yields
        ------
        str
            CHAT data string for one file.
        """
        header_first = (
            "UTF8",
            "PID",
            "Languages",
            "Participants",
            "Date",
            "Types",
        )

        for f in self._files:
            str_for_file = ""

            header_keys = _sort_keys(f.header.keys(), first=header_first)

            for key in header_keys:
                if key == "Languages":
                    str_for_file += (
                        f"@Languages:\t{' , '.join(f.header['Languages'])}\n"
                    )
                elif key == "Participants":
                    participants = f.header["Participants"]

                    parts = []
                    for code, demographics in participants.items():
                        parts.append(
                            f"{code} {demographics['name']} {demographics['role']}"
                        )
                    str_for_file += f"@Participants:\t{' , '.join(parts)}\n"

                    for code, d in participants.items():
                        # d = demographics
                        id_line = (
                            f"{d['language']}|"
                            f"{d['corpus']}|"
                            f"{code}|"
                            f"{d['age']}|"
                            f"{d['sex']}|"
                            f"{d['group']}|"
                            f"{d['ses']}|"
                            f"{d['role']}|"
                            f"{d['education']}|"
                            f"{d['custom']}|"
                        )
                        str_for_file += f"@ID:\t{id_line}\n"

                elif key == "Date":
                    # TODO: A CHAT file may have more than one recording date.
                    try:
                        date = sorted(f.header["Date"])[0]
                    except IndexError:
                        continue
                    str_for_file += f"@Date:\t{date.strftime('%d-%b-%Y').upper()}\n"

                elif f.header[key]:
                    str_for_file += f"@{key}:\t{f.header[key]}\n"

                else:
                    str_for_file += f"@{key}\n"

            for u in f.utterances:
                str_for_file += u._to_str(tabular=tabular)

            yield str_for_file

    @_params_in_docstring("participants", "exclude")
    def head(self, n: int = 5, participants=None, exclude=None):
        """Return the first several utterances.

        Parameters
        ----------
        n : int, optional
            The number of utterances to return.

        Returns
        -------
        list of utterances
        """
        return self._head_or_tail(slice(n), participants, exclude)

    @_params_in_docstring("participants", "exclude")
    def tail(self, n: int = 5, participants=None, exclude=None):
        """Return the last several utterances.

        Parameters
        ----------
        n : int, optional
            The number of utterances to return.

        Returns
        -------
        list of utterances
        """
        return self._head_or_tail(slice(-n, None), participants, exclude)

    def _head_or_tail(self, slice_, participants, exclude):
        us = self.utterances(
            participants=participants, exclude=exclude, by_files=False
        ).__getitem__(slice_)
        return _list(us)

    def _get_info_summary(self) -> str:
        lines = [
            f"{len(self._files)} files",
            f"{sum(len(f.utterances) for f in self._files)} utterances",
            f"{sum(len(u.tokens) for f in self._files for u in f.utterances)} words",
        ]
        return "\n".join(lines)

    def _get_info_details_of_file(self, f: _File) -> Dict:
        result = {
            "Utterance Count": len(f.utterances),
            "Word Count": sum(len(u.tokens) for u in f.utterances),
        }
        if not _is_uuid(f.file_path):
            result["File Path"] = f.file_path
        return result

    def info(self, verbose=False) -> None:
        """Print a summary of this Reader's data.

        Parameters
        ----------
        verbose : bool, optional
            If ``True`` (default is ``False``), show the details of all the files.
        """
        print(self._get_info_summary())
        if len(self._files) < 2:
            return
        details = [self._get_info_details_of_file(f) for f in self._files]
        max_n_files_if_not_verbose = 5
        if not verbose:
            details = details[:max_n_files_if_not_verbose]
            n_files = max_n_files_if_not_verbose
        else:
            n_files = self.n_files()
        indices = (f"#{i + 1}" for i in range(n_files))
        output = tabulate(details, headers="keys", showindex=indices)
        if not verbose:
            output += "\n...\n(set `verbose` to True for all the files)"
        print(output)

    def to_chat(
        self,
        path: str,
        is_dir: bool = False,
        filenames: Iterable[str] = None,
        tabular: bool = True,
        encoding: str = _ENCODING,
    ) -> None:
        """Export to CHAT data files.

        Parameters
        ----------
        path : str
            The path to a file where you want to output the CHAT data,
            e.g., `"data.cha"`, `"foo/bar/data.cha"`.
        is_dir : bool, optional
            If ``True`` (default is ``False``), then ``path`` is interpreted as a
            directory instead.
            The CHAT data is written to possibly multiple files under this directory.
            The number of files you get can be checked by calling
            :func:`~pylangacq.Reader.n_files`, which depends on how this reader
            object is created.
        filenames : Iterable[str], optional
            Used only when ``is_dir`` is ``True``.
            These are the filenames of the CHAT files to write.
            If ``None`` or not given, {0001.cha, 0002.cha, ...} are used.
        tabular : bool, optional
            If ``True``, adjust spacing such that the three tiers of the utterance,
            %mor, and %gra are aligned in a tabular form. Note that such alignment
            would drop annotations (e.g., pauses) on the main utterance tier.
        encoding : str, optional
            Text encoding to output the CHAT data as. The default value is ``"utf-8"``
            for Unicode UTF-8.

        Raises
        ------
        ValueError
            - If you attempt to output data to a single local file, but the CHAT
              data in this reader appears to be organized in multiple files.
            - If you attempt to output data to a directory while providing your own
              filenames, but the number of your filenames doesn't match
              the number of CHAT files in this reader object.
        """
        if not is_dir:
            if self.n_files() > 1:
                raise ValueError(
                    "The CHAT data in this reader object exists in more than one file. "
                    "(Call the `.n_files()` method to check.) It is not possible to "
                    "output data from multiple files to a single local file. "
                    "To output data, set `is_dir` to `True`, and pass in a directory "
                    "(not a file path) to `path`."
                )
            dir_, basename = os.path.split(path)
            if not basename and dir_.endswith(os.sep):
                raise ValueError(
                    f"You've passed in {dir_} as `path` that looks like a directory "
                    f"instead of a path to a file, because {dir_} ends with the "
                    f"directory separator {os.sep}. "
                    "As an example, a path to a file should look like "
                    f"foo{os.sep}bar.cha"
                )
            elif not basename:
                raise ValueError(
                    f"You've passed in {dir_} as `path`, but it doesn't look like "
                    "a path to a file."
                )
            filenames = [basename]
        else:
            dir_ = path
            if filenames is None:
                filenames = [
                    f"{str(i + 1).zfill(4)}.cha" for i in range(len(self._files))
                ]
            else:
                filenames = list(filenames)
            if len(filenames) != len(self._files):
                raise ValueError(
                    f"There are {len(self._files)} CHAT files to create, "
                    f"but you've provided {len(filenames)} filenames."
                )
        if dir_:
            os.makedirs(dir_, exist_ok=True)
        for filename, lines in zip(filenames, self.to_strs(tabular=tabular)):
            with open(os.path.join(dir_, filename), "w", encoding=encoding) as f:
                f.write(lines)

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
            preclitic_indices = []
            postclitic_indices = []

            mor_items = []
            if "%mor" in tiermarker_to_line:
                mor_split = tiermarker_to_line["%mor"].split()

                for j, item in enumerate(mor_split):
                    match = _CLITIC_REGEX.search(item)
                    _, morph_preclitic, morph_core, _, morph_postclitic = match.groups()

                    if morph_preclitic:
                        for morph in morph_preclitic.split("$"):
                            preclitic_indices.append(len(mor_items))
                            mor_items.append(morph)

                    mor_items.append(morph_core)

                    if morph_postclitic:
                        for morph in morph_postclitic.split("~"):
                            postclitic_indices.append(len(mor_items))
                            mor_items.append(morph)

            if mor_items and (
                (len(forms) + len(preclitic_indices) + len(postclitic_indices))
                != len(mor_items)
            ):
                raise ValueError(
                    "cannot align the utterance and %mor tiers:\n"
                    f"Tiers --\n{tiermarker_to_line}\n"
                    f"Cleaned-up utterance --\n{utterance_line}\n"
                    f"Parsed %mor tier --\n{mor_items}"
                )

            # %gra tier
            gra_items = (
                tiermarker_to_line["%gra"].split()
                if "%gra" in tiermarker_to_line
                else []
            )

            if mor_items and gra_items and (len(mor_items) != len(gra_items)):
                raise ValueError(
                    f"cannot align the %mor and %gra tiers:\n"
                    f"Tiers --\n{tiermarker_to_line}\n"
                    f"Parsed %mor tier --\n{mor_items}\n"
                    f"parsed %gra tier --\n{gra_items}"
                )

            # utterance tier
            if mor_items and (preclitic_indices or postclitic_indices):
                word_iterator = iter(forms)
                utterance_items = [""] * len(mor_items)

                for j in range(len(mor_items)):
                    if j in postclitic_indices:
                        utterance_items[j] = _POSTCLITIC
                    elif j in preclitic_indices:
                        utterance_items[j] = _PRECLITIC
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
        headname_to_entry = {}

        for line in lines:
            header_re_search = _HEADER_REGEX.search(line)
            if not header_re_search:
                continue

            if line.startswith("@Begin") or line.startswith("@End"):
                continue

            # find head, e.g., "Languages", "Participants", "ID" etc
            head = header_re_search.group(1)
            line = header_re_search.group(3)

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
                    if "Participants" not in headname_to_entry:
                        headname_to_entry["Participants"] = {}
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

                if "Participants" not in headname_to_entry:
                    headname_to_entry["Participants"] = {}
                if code not in headname_to_entry["Participants"]:
                    headname_to_entry["Participants"][code] = {}

                headname_to_entry["Participants"][code].update(head_to_info)

            elif head == "Date":
                try:
                    date = self._header_line_to_date(line.strip())
                except (TypeError, ValueError, ParserError):
                    continue
                if "Date" not in headname_to_entry:
                    headname_to_entry["Date"] = set()
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
                headname_to_entry[head] = line or ""

        return headname_to_entry if any(headname_to_entry.values()) else {}

    @staticmethod
    def _header_line_to_date(line: str) -> datetime.date:
        return parse_date(line).date()

    @staticmethod
    def _get_lines(raw_str: str) -> List[str]:
        lines: List[str] = []
        raw_str = (raw_str or "").strip()

        if not raw_str:
            return lines

        for line in raw_str.splitlines():
            line = line.strip()
            if not line:
                continue

            # TODO: Why did I do this?
            if line.startswith("%xpho:") or line.startswith("%xmod:"):
                line = line.replace("%x", "%", 1)

            if line[0] not in _CHAT_LINE_INDICATORS:
                previous_line = lines.pop()
                line = f"{previous_line} {line}"

            lines.append(line)

        return lines


def _get_uuid() -> str:
    """This function goes hand-in-hand with _is_uuid() below."""
    return str(uuid.uuid4())


def _is_uuid(s: str) -> bool:
    """This function goes hand-in-hand with _get_uuid() above."""
    # Implementation from https://stackoverflow.com/a/33245493
    try:
        uuid_obj = uuid.UUID(s, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == s


def _initialize_cached_data_dir() -> None:
    if os.path.isdir(_CACHED_DATA_DIR):
        shutil.rmtree(_CACHED_DATA_DIR)
    os.makedirs(_CACHED_DATA_DIR)
    with open(os.path.join(_CACHED_DATA_DIR, "README.txt"), "w", encoding="utf-8") as f:
        f.write(
            "The contents of this directory are automatically managed by "
            "the PyLangAcq library. Please do not edit anything on your own.\n"
        )
    with open(_CACHED_DATA_JSON_PATH, "w", encoding="utf-8") as f:
        f.write("{}")


def _write_cached_data_json(records: Dict) -> None:
    with open(_CACHED_DATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)


def cached_data_info() -> Set[str]:
    """Return the information of the cached datasets.

    Returns
    -------
    Set[str]
        A set of the URLs for the cached CHILDES / TalkBank datasets.
    """
    try:
        existing_records = json.load(open(_CACHED_DATA_JSON_PATH, encoding="utf-8"))
    except FileNotFoundError:
        return set()
    else:
        return set(existing_records.keys())


def remove_cached_data(url: str = None) -> None:
    """Remove data cached on disk.

    Parameters
    ----------
    url : str, optional
        If provided, remove only the data specified by this URL. If not provided,
        all cached data is removed.
    """
    try:
        existing_records = json.load(open(_CACHED_DATA_JSON_PATH, encoding="utf-8"))
    except FileNotFoundError:
        _initialize_cached_data_dir()
        return
    if url is None:
        for subdir in [record["subdir"] for record in existing_records.values()]:
            shutil.rmtree(os.path.join(_CACHED_DATA_DIR, subdir))
        _initialize_cached_data_dir()
    else:
        subdir = existing_records.get(url, {}).get("subdir")
        if subdir:
            del existing_records[url]
            _write_cached_data_json(existing_records)
            shutil.rmtree(os.path.join(_CACHED_DATA_DIR, subdir))
        else:
            raise KeyError(f"url not found among the cached data: {url}")


@_params_in_docstring("match", "exclude", "encoding", "cls", class_method=False)
def read_chat(
    path: str,
    match: str = None,
    exclude: str = None,
    encoding: str = _ENCODING,
    cls: type = Reader,
) -> "pylangacq.Reader":
    """Create a reader of CHAT data.

    If ``path`` is a remote ZIP file and you expect to call this function
    with the same path multiple times, consider downloading the data to the local
    system and then reading it from there to avoid unnecessary re-downloading.
    Caching a remote ZIP file isn't implemented (yet) as the upstream CHILDES /
    TalkBank data is updated in minor ways from time to time.

    Parameters
    ----------
    path : str
        A path that points to one of the following:

        - ZIP file. Either a local ``.zip`` file path or a URL (one that begins with
          ``"https://"`` or ``"http://"``).
          Example of a URL: ``"https://childes.talkbank.org/data/Eng-NA/Brown.zip"``
        - A local directory, for files under this directory recursively.
        - A single ``.cha`` CHAT file.

    Returns
    -------
    :class:`~pylangacq.Reader`
    """
    if cls != Reader and not issubclass(cls, Reader):
        raise TypeError(f"Only a Reader class or its child class is allowed: {cls}")

    # Just in case the user provides a CHILDES web link like
    # https://childes.talkbank.org/access/Eng-NA/Brown.html
    # instead of https://childes.talkbank.org/data/Eng-NA/Brown.zip.
    # The subdomain can be "childes", "phonbank", "ca", etc.
    # This hack is just for convenience.
    # Not sure if we should encourage using the .html link,
    # since I can't guarantee the URL format...
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
            f"{{.zip file, local directory, .cha file}}: {path}"
        )


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


class _HTTPSession(requests.Session):
    def __init__(
        self, max_retries: int = 10, backoff_factor: float = 0.1, timeout: int = 10
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


def _download_file(url, path, session=None):
    if session is None:
        session = _HTTPSession()
    with open(path, "wb") as f, session.get(url, stream=True) as r:
        shutil.copyfileobj(r.raw, f)
