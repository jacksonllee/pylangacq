"""Interfacing with CHAT data files."""

import sys
import os
import fnmatch
import re
import tempfile
import uuid
import io
from pprint import pformat
from collections import Counter
from itertools import chain
from functools import wraps

from pylangacq.measures import get_MLUm, get_MLUw, get_TTR, get_IPSyn
from pylangacq.util import (
    ENCODING,
    CLITIC,
    get_participant_code,
    convert_date_to_tuple,
    clean_utterance,
    clean_word,
    get_lemma_from_mor,
    get_time_marker,
)


_TEMP_DIR = tempfile.mkdtemp()


def read_chat(*filenames, **kwargs):
    """Create a ``Reader`` object with CHAT data files.

    Parameters
    ----------
    filenames : str or iterable or str, optional
        One or more filenames. A filename may match exactly a CHAT file
        (e.g., ``'eve01.cha'``) or matches multiple files by glob patterns
        (e.g., ``'eve*.cha'``, for ``'eve01.cha'``, ``'eve02.cha'``, etc.).
        ``*`` matches any number (including zero) of characters, while
        ``?`` matches exactly one character.
        A filename can be either an absolute or relative path.
        If no *filenames* are provided, an empty Reader instance is created.
    kwargs
        Only the keyword ``encoding`` is recognized, which defaults
        to 'utf8'. (New in version 0.9)

    Returns
    -------
    Reader
    """
    # TODO: Should error if any of "filenames" give no actual filenames?
    return Reader.from_chat_files(*filenames, **kwargs)


def params_in_docstring(*params):
    docstring = ""
    if "participant" in params:
        docstring += """
        participant : str or iterable of str, optional
            Participants of interest.
            If unspecified or ``None``, all participants are included."""
    if "exclude" in params:
        docstring += """
        exclude : str or iterable of str, optional
            Participants to exclude.
            If unspecified or ``None``, no participants are excluded."""
    if "by_files" in params:
        docstring += """
        by_files : bool, optional
            If ``True``, return dict(absolute-path filename: X for that file)
            instead of X for all files altogether."""
    if "keep_case" in params:
        docstring += """
        keep_case : bool, optional
            If ``True`` (the default), case distinctions are kept, e.g.,
            word tokens like "the" and "The" are treated as distinct.
            If ``False``, all word tokens are forced to be in lowercase."""

    def real_decorator(func):
        returns_header = "\n\n        Returns\n        -------"
        func.__doc__ = func.__doc__.replace(returns_header, docstring + returns_header)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return real_decorator


class Reader(object):
    """A class for reading multiple CHAT files.

    Parameters
    ----------
    filenames : str or iterable or str, optional
        One or more filenames. A filename may match exactly a CHAT file
        (e.g., ``'eve01.cha'``) or matches multiple files by glob patterns
        (e.g., ``'eve*.cha'``, for ``'eve01.cha'``, ``'eve02.cha'``, etc.).
        ``*`` matches any number (including zero) of characters, while
        ``?`` matches exactly one character.
        A filename can be either an absolute or relative path.
        If no *filenames* are provided, an empty Reader instance is created.
    kwargs
        Only the keyword ``encoding`` is recognized, which defaults
        to 'utf8'. (New in version 0.9)
    """

    def __init__(self, *filenames, **kwargs):
        self.encoding = kwargs.get("encoding", ENCODING)
        self._input_filenames = filenames
        self._reset_reader(*self._input_filenames)

    @classmethod
    def from_chat_str(cls, chat_str, encoding=ENCODING):
        """Create a ``Reader`` object with CHAT data as a string.

        Parameters
        ----------
        chat_str : str
            CHAT data as an in-memory string. It would be what a single
            CHAT data file contains.
        encoding
            Encoding of the CHAT data

        Returns
        -------
        Reader
        """
        file_path = os.path.join(_TEMP_DIR, str(uuid.uuid4()))
        with open(file_path, mode="w", encoding=encoding) as f:
            f.write(chat_str)
        return cls(file_path, encoding=encoding)

    @classmethod
    def from_chat_files(cls, *filenames, **kwargs):
        """Create a ``Reader`` object with CHAT data files.

        Parameters
        ----------
        filenames : str or iterable or str, optional
            One or more filenames. A filename may match exactly a CHAT file
            (e.g., ``'eve01.cha'``) or matches multiple files by glob patterns
            (e.g., ``'eve*.cha'``, for ``'eve01.cha'``, ``'eve02.cha'``, etc.).
            ``*`` matches any number (including zero) of characters, while
            ``?`` matches exactly one character.
            A filename can be either an absolute or relative path. If
            no *filenames* are provided, an empty Reader instance is created.
        kwargs
            Only the keyword ``encoding`` is recognized, which defaults
            to 'utf8'. (New in version 0.9)

        Returns
        -------
        Reader

        Notes
        -----
        Because CHAT data most likely comes as files on disk,
        an equivalent library top-level function ``pylangacq.read_chat``
        is defined for convenience.
        """
        return cls(*filenames, **kwargs)

    @staticmethod
    def _get_abs_filenames(*filenames):
        """Return the set of absolute-path filenames based on filenames."""
        if sys.platform.startswith("win"):
            windows = True  # pragma: no cover
        else:
            windows = False

        filenames_set = set()
        for filename in filenames:
            if not isinstance(filename, str):
                raise ValueError("{} is not str".format(repr(filename)))

            if windows:
                filename = filename.replace("/", os.sep)  # pragma: no cover
            else:
                filename = filename.replace("\\", os.sep)

            abs_fullpath = os.path.abspath(filename)
            abs_dir = os.path.dirname(abs_fullpath)
            glob_match_pattern = re.compile(r".*[\*\?\[\]].*")
            while glob_match_pattern.search(abs_dir):  # pragma: no cover
                abs_dir = os.path.dirname(abs_dir)

            if not os.path.isdir(abs_dir):  # pragma: no cover
                msg = (
                    f"{abs_dir} is not a directory. "
                    f"Filename {filename} is likely invalid."
                )
                raise ValueError(msg)

            candidate_filenames = [
                os.path.join(dir_, fn)
                for dir_, _, fns in os.walk(abs_dir)
                for fn in fns
            ]

            filenames_set.update(fnmatch.filter(candidate_filenames, abs_fullpath))
        return filenames_set

    def _reset_reader(self, *filenames, **kwargs):
        check = kwargs.get("check", True)
        filenames_set = set()

        if not check:
            filenames_set = set(filenames)
        elif filenames:
            filenames_set = self._get_abs_filenames(*filenames)

        self._filenames = filenames_set
        self._all_part_of_speech_tags = None

        self._fname_to_reader = {}
        for fn in self._filenames:
            # TODO rewrite what _SingleReader takes as args
            self._fname_to_reader[fn] = _SingleReader(fn, encoding=self.encoding)

    def __len__(self):
        """Return the number of files.

        Returns
        -------
        int
        """
        return len(self._filenames)

    def filenames(self, sorted_by_age=False):
        """Return the set of absolute-path filenames.

        Parameters
        ----------
        sorted_by_age : bool, optional
            Whether to return the filenames as a list sorted by the target
            child's age.

        Returns
        -------
        set of str or list of str
        """
        if not sorted_by_age:
            return self._filenames
        else:
            # sort by filename first (so filenames with same age are sorted)
            return [
                fn for fn, _ in sorted(sorted(self.age().items()), key=lambda x: x[1])
            ]

    def number_of_files(self):
        """Return the number of files.

        Returns
        -------
        int
        """
        return len(self)

    @params_in_docstring("participant", "exclude", "by_files")
    def number_of_utterances(self, participant=None, exclude=None, by_files=False):
        """Return the number of utterances for *participant* in all files.

        Parameters
        ----------

        Returns
        -------
        int or dict(str: int)
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].number_of_utterances(
                    participant=participant, exclude=exclude
                )
                for fn in self._filenames
            }
        else:
            return sum(
                self._fname_to_reader[fn].number_of_utterances(
                    participant=participant, exclude=exclude
                )
                for fn in self._filenames
            )

    def headers(self):
        """Return a dict mapping a file path to the headers of that file.

        Returns
        -------
        dict(str: dict)
        """
        return {fn: self._fname_to_reader[fn].headers() for fn in self._filenames}

    def index_to_tiers(self):
        """Return a dict mapping a file path to the file's index_to_tiers dict.

        Returns
        -------
        dict(str: dict)
        """
        return {
            fn: self._fname_to_reader[fn].index_to_tiers() for fn in self._filenames
        }

    def participants(self):
        """Return a dict mapping a file path to the file's participant info.

        Returns
        -------
        dict(str: dict)
        """
        return {fn: self._fname_to_reader[fn].participants() for fn in self._filenames}

    @params_in_docstring("by_files")
    def participant_codes(self, by_files=False):
        """Return the participant codes (e.g., ``{'CHI', 'MOT'}``).

        Parameters
        ----------

        Returns
        -------
        set(str) or dict(str: set(str))
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].participant_codes()
                for fn in self._filenames
            }
        else:
            output_set = set()
            for fn in self._filenames:
                for code in self._fname_to_reader[fn].participant_codes():
                    output_set.add(code)
            return output_set

    def languages(self):
        """Return a map from a file path to the languages used.

        Returns
        -------
        dict(str: list(str))
        """
        return {fn: self._fname_to_reader[fn].languages() for fn in self._filenames}

    def dates_of_recording(self):
        """Return a map from a file path to the date of recording.

        The date of recording is in the form of (year, month, day).

        Returns
        -------
        dict(str: list(tuple(int, int, int)))
        """
        return {
            fn: self._fname_to_reader[fn].dates_of_recording() for fn in self._filenames
        }

    def date_of_birth(self):
        """Return a map from a file path to the date of birth.

        Returns
        -------
        dict(str: dict(str: tuple(int, int, int)))
        """
        return {fn: self._fname_to_reader[fn].date_of_birth() for fn in self._filenames}

    def age(self, participant="CHI", months=False):
        """Return a map from a file path to the *participant*'s age.

        The age is in the form of (years, months, days).

        Parameters
        ----------
        participant : str, optional
            The specified participant
        months : bool, optional
            If ``True``, age is in months.

        Returns
        -------
        dict(str: tuple(int, int, int)) or dict(str: float)
        """
        return {
            fn: self._fname_to_reader[fn].age(participant=participant, months=months)
            for fn in self._filenames
        }

    def abspath(self, basename):
        """Return the absolute path of ``basename``.

        Parameters
        ----------
        basename : str
            The basename (e.g., "foobar.cha") of the desired data file.

        Returns
        -------
        str
        """
        # TODO: tests
        for file_path in self._filenames:
            if os.path.basename(file_path) == basename:
                return file_path
        else:
            raise ValueError("No such file.")

    @params_in_docstring("participant", "exclude", "by_files")
    def utterances(self, participant=None, exclude=None, clean=True, by_files=False):
        """Return a list of (*participant*, utterance) pairs from all files.

        Parameters
        ----------
        clean : bool, optional
            Whether to filter away the CHAT annotations in the utterance.

        Returns
        -------
        list(str) or dict(str: list(str))
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].utterances(
                    participant=participant, exclude=exclude, clean=clean
                )
                for fn in self._filenames
            }
        else:
            return list(
                chain.from_iterable(
                    self._fname_to_reader[fn].utterances(
                        participant=participant, exclude=exclude, clean=clean
                    )
                    for fn in sorted(self._filenames)
                )
            )

    @params_in_docstring("participant", "exclude", "keep_case", "by_files")
    def word_frequency(
        self, participant=None, exclude=None, keep_case=True, by_files=False
    ):
        """Return a word frequency counter for *participant* in all files.

        Parameters
        ----------

        Returns
        -------
        Counter, or dict(str: Counter)
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].word_frequency(
                    participant=participant,
                    exclude=exclude,
                    keep_case=keep_case,
                )
                for fn in self._filenames
            }
        else:
            output_counter = Counter()
            for fn in self._filenames:
                output_counter.update(
                    self._fname_to_reader[fn].word_frequency(
                        participant=participant,
                        exclude=exclude,
                        keep_case=keep_case,
                    )
                )
            return output_counter

    @params_in_docstring("participant", "exclude", "by_files")
    def words(self, participant=None, exclude=None, by_files=False):
        """Return a list of words by *participant* in all files.

        Parameters
        ----------

        Returns
        -------
        list(str) or dict(str: list(str))
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].words(
                    participant=participant, exclude=exclude
                )
                for fn in self._filenames
            }
        else:
            return list(
                chain.from_iterable(
                    self._fname_to_reader[fn].words(
                        participant=participant, exclude=exclude
                    )
                    for fn in sorted(self._filenames)
                )
            )

    @params_in_docstring("participant", "exclude", "by_files")
    def tagged_words(self, participant=None, exclude=None, by_files=False):
        """Return a list of tagged words by *participant* in all files.

        Parameters
        ----------

        Returns
        -------
        list(tuple) or dict(str: list(tuple))
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].tagged_words(
                    participant=participant, exclude=exclude
                )
                for fn in self._filenames
            }
        else:
            return list(
                chain.from_iterable(
                    self._fname_to_reader[fn].tagged_words(
                        participant=participant, exclude=exclude
                    )
                    for fn in sorted(self._filenames)
                )
            )

    @params_in_docstring("participant", "exclude", "by_files")
    def sents(self, participant=None, exclude=None, by_files=False):
        """Return a list of sents by *participant* in all files.

        Parameters
        ----------

        Returns
        -------
        list(list(str)) or dict(str: list(list(str)))
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].sents(
                    participant=participant, exclude=exclude
                )
                for fn in self._filenames
            }
        else:
            return list(
                chain.from_iterable(
                    self._fname_to_reader[fn].sents(
                        participant=participant, exclude=exclude
                    )
                    for fn in sorted(self._filenames)
                )
            )

    @params_in_docstring("participant", "exclude", "by_files")
    def tagged_sents(self, participant=None, exclude=None, by_files=False):
        """Return a list of tagged sents by *participant* in all files.

        Parameters
        ----------

        Returns
        -------
        list(list(tuple)) or dict(str: list(list(tuple)))
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].tagged_sents(
                    participant=participant, exclude=exclude
                )
                for fn in self._filenames
            }
        else:
            return list(
                chain.from_iterable(
                    self._fname_to_reader[fn].tagged_sents(
                        participant=participant, exclude=exclude
                    )
                    for fn in sorted(self._filenames)
                )
            )

    @params_in_docstring("participant", "exclude", "by_files")
    def part_of_speech_tags(self, participant=None, exclude=None, by_files=False):
        """Return the part-of-speech tags in the data for *participant*.

        Parameters
        ----------

        Returns
        -------
        set or dict(str: set)
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].part_of_speech_tags(
                    participant=participant, exclude=exclude
                )
                for fn in self._filenames
            }
        else:
            return set().union(
                *(
                    self._fname_to_reader[fn].part_of_speech_tags(
                        participant=participant, exclude=exclude
                    )
                    for fn in self._filenames
                )
            )

    def update(self, reader):
        """Combine the current CHAT Reader instance with ``reader``.

        Parameters
        ----------
        reader : Reader
        """
        if type(reader) is Reader:
            add_filenames = reader.filenames()
        else:
            raise ValueError("invalid reader")

        new_filenames = add_filenames | self.filenames()
        self._reset_reader(*tuple(new_filenames), check=False)

    def add(self, *filenames):
        """Add one or more CHAT ``filenames`` to the current reader.

        Parameters
        ----------
        *filenames
            Filenames may take glob patterns with wildcards ``*`` and ``?``.
        """
        add_filenames = self._get_abs_filenames(*filenames)
        if not add_filenames:
            raise ValueError("No files to add!")
        new_filenames = self.filenames() | add_filenames
        self._reset_reader(*tuple(new_filenames), check=False)

    def remove(self, *filenames):
        """Remove one or more CHAT ``filenames`` from the current reader.

        Parameters
        ----------
        *filenames
            Filenames may take glob patterns with wildcards ``*`` and ``?``.
        """
        remove_filenames = self._get_abs_filenames(*filenames)
        if not remove_filenames:
            raise ValueError("No files to remove!")
        new_filenames = set(self.filenames())

        for remove_filename in remove_filenames:
            if remove_filename not in self.filenames():
                raise ValueError("filename not found")
            else:
                new_filenames.remove(remove_filename)

        self._reset_reader(*tuple(new_filenames), check=False)

    def clear(self):
        """Clear everything and reset as an empty Reader instance."""
        self._reset_reader()

    @params_in_docstring("participant", "exclude", "keep_case", "by_files")
    def word_ngrams(
        self, n, participant=None, exclude=None, keep_case=True, by_files=False
    ):
        """Return a word ``n``-gram counter by ``participant`` in all files.

        Returns
        -------
        Counter, or dict(str: Counter)
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].word_ngrams(
                    n,
                    participant=participant,
                    exclude=exclude,
                    keep_case=keep_case,
                )
                for fn in self._filenames
            }
        else:
            output_counter = Counter()
            for fn in self._filenames:
                output_counter.update(
                    self._fname_to_reader[fn].word_ngrams(
                        n,
                        participant=participant,
                        exclude=exclude,
                        keep_case=keep_case,
                    )
                )
            return output_counter

    def MLU(self, participant="CHI"):
        """Return a map from a file path to the file's MLU by morphemes.

        MLU = mean length of utterance. This method is identical to ``MLUm``.

        Parameters
        ----------
        participant : str, optional
            The specified participant (default to ``'CHI'``).

        Returns
        -------
        dict(str: float)
        """
        return {
            fn: self._fname_to_reader[fn].MLU(participant=participant)
            for fn in self._filenames
        }

    def MLUm(self, participant="CHI"):
        """Return a map from a file path to the file's MLU by morphemes.

        MLU = mean length of utterance. This method is identical to ``MLUm``.

        Parameters
        ----------
        participant : str, optional
            The specified participant (default to ``'CHI'``).

        Returns
        -------
        dict(str: float)
        """
        return {
            fn: self._fname_to_reader[fn].MLUm(participant=participant)
            for fn in self._filenames
        }

    def MLUw(self, participant="CHI"):
        """Return a map from a file path to the file's MLU by words.

        MLU = mean length of utterance.

        Parameters
        ----------
        participant : str, optional
            The specified participant (default to ``'CHI'``).

        Returns
        -------
        dict(str: float)
        """
        return {
            fn: self._fname_to_reader[fn].MLUw(participant=participant)
            for fn in self._filenames
        }

    def TTR(self, participant="CHI"):
        """Return a map from a file path to the file's TTR.

        TTR = type-token ratio

        Parameters
        ----------
        participant : str, optional
            The specified participant (default to ``'CHI'``).

        Returns
        -------
        dict(str: float)
        """
        return {
            fn: self._fname_to_reader[fn].TTR(participant=participant)
            for fn in self._filenames
        }

    def IPSyn(self, participant="CHI"):
        """Return a map from a file path to the file's IPSyn.

        IPSyn = index of productive syntax

        Parameters
        ----------
        participant : str, optional
            The specified participant (default to ``'CHI'``).

        Returns
        -------
        dict(str: int)
        """
        return {
            fn: self._fname_to_reader[fn].IPSyn(participant=participant)
            for fn in self._filenames
        }

    @params_in_docstring("participant", "exclude", "by_files")
    def search(
        self,
        search_item,
        participant=None,
        exclude=None,
        match_entire_word=True,
        lemma=False,
        output_tagged=True,
        output_sents=True,
        by_files=False,
    ):
        """Return a list of elements containing *search_item* by *participant*.

        Parameters
        ----------
        search_item : str
            Word or lemma to search for.
        match_entire_word : bool, optional
            Whether to match for the entire word.
        lemma : bool, optional
            Whether the ``search_item`` refers to the lemma (from "mor" in the
            tagged word) instead.
        output_tagged : bool, optional
            Whether a word in the return object is a tagged word of the
            (word, pos, mor, rel) tuple; otherwise just a word string.
        output_sents : bool, optional
            Whether each element in the return object is a list for each
            utterance; otherwise each element is a word (tagged or untagged)
            without the utterance structure.

        Returns
        -------
        list or dict(str: list)
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].search(
                    search_item,
                    participant=participant,
                    exclude=exclude,
                    match_entire_word=match_entire_word,
                    lemma=lemma,
                    output_tagged=output_tagged,
                    output_sents=output_sents,
                )
                for fn in self._filenames
            }
        else:
            output_list = []
            for fn in self.filenames(sorted_by_age=True):
                output_list.extend(
                    self._fname_to_reader[fn].search(
                        search_item,
                        participant=participant,
                        exclude=exclude,
                        match_entire_word=match_entire_word,
                        lemma=lemma,
                        output_tagged=output_tagged,
                        output_sents=output_sents,
                    )
                )
            return output_list

    @params_in_docstring("participant", "exclude", "by_files")
    def concordance(
        self,
        search_item,
        participant=None,
        exclude=None,
        match_entire_word=True,
        lemma=False,
        by_files=False,
    ):
        """Return a list of utterances with *search_item* for *participant*.

        All strings are aligned for *search_item* by space
        padding to create the word concordance effect.

        Parameters
        ----------
        search_item : str
            Word or lemma to search for.
        match_entire_word : bool, optional
            If False (default: True), substring matching is performed.
        lemma : bool, optional
            If True (default: False), *search_item* refers to the
            lemma (from "mor" in the tagged word) instead.

        Returns
        -------
        list, or dict(str: list)
        """
        if by_files:
            return {
                fn: self._fname_to_reader[fn].concordance(
                    search_item,
                    participant=participant,
                    exclude=exclude,
                    match_entire_word=match_entire_word,
                    lemma=lemma,
                )
                for fn in self._filenames
            }
        else:
            output_list = []
            for fn in self.filenames(sorted_by_age=True):
                output_list.extend(
                    self._fname_to_reader[fn].concordance(
                        search_item,
                        participant=participant,
                        exclude=exclude,
                        match_entire_word=match_entire_word,
                        lemma=lemma,
                    )
                )
            return output_list


class _SingleReader(object):
    """A class for reading a single CHAT file."""

    def __init__(self, filename=None, str_=None, encoding=ENCODING):

        self.encoding = encoding

        if (filename and str_) or (filename is None and str_ is None):
            msg = (
                "_SingleReader is initialized by either one CHAT file or "
                "one CHAT str (but not both)"
            )
            raise ValueError(msg)

        self._filename = os.path.abspath(filename) if filename else None
        self._str = str_

        if not os.path.isfile(self._filename):
            raise FileNotFoundError(self._filename)

        self._headers = self._get_headers()
        self._index_to_tiers = self._get_index_to_tiers()
        self.tier_markers = self._tier_markers()

        self._part_of_speech_tags = None

        # list of (partcipant, list of tagged sents)
        self._all_tagged_sents = self._create_all_tagged_sents()

        # for MLUw() and TTR()
        self.words_to_ignore = {
            "",
            "!",
            "+...",
            ".",
            ",",
            "?",
            "‡",
            "„",
            "0",
            CLITIC,
        }

        # for MLUm()
        self.pos_to_ignore = {"", "!", "+...", "0", "?", "BEG"}

    def __len__(self):
        return len(self._index_to_tiers)

    def number_of_utterances(self, participant=None, exclude=None):
        return len(self.utterances(participant=participant, exclude=exclude))

    def filename(self):
        return self._filename

    def _get_file_object(self):
        if self._filename:
            return open(self._filename, mode="r", encoding=self.encoding)
        else:
            return io.TextIOWrapper(
                io.BytesIO(self._str.encode()), encoding=self.encoding
            )

    def cha_lines(self):
        """A generator of lines in the CHAT file,
        with the tab-character line continuations undone.
        """
        previous_line = ""

        for line in self._get_file_object():
            previous_line = previous_line.strip()
            current_line = line.rstrip()  # don't remove leading \t

            if not current_line:
                continue

            if current_line.startswith("%xpho:") or current_line.startswith("%xmod:"):
                current_line = current_line.replace("%x", "%", 1)

            if previous_line and current_line.startswith("\t"):
                previous_line = "{} {}".format(
                    previous_line, current_line.strip()
                )  # strip \t
            elif previous_line:
                yield previous_line
                previous_line = current_line
            else:  # when it's the very first line
                previous_line = current_line
        yield previous_line  # don't forget the very last line!

    def _tier_markers(self):
        """Determine what the %-tiers are."""
        result = set()
        for tiermarkers_to_tiers in self._index_to_tiers.values():
            for tier_marker in tiermarkers_to_tiers.keys():
                if tier_marker.startswith("%"):
                    result.add(tier_marker)
        return result

    def index_to_tiers(self):
        """
        Return a dict of utterances and the corresponding tiers.

        :return: A dict where key is utterance index (starting from 0)
            and value is a dict,
            where key is tier marker and value is the line as str. For example,
            two key-value pairs in the output dict may look like this::

                 1537: {'%gra': '1|2|MOD 2|0|INCROOT 3|2|PUNCT',
                        '%mor': 'n|tapioca n|finger .',
                        'CHI': 'tapioca finger . [+ IMIT]'},
                 1538: {'%gra': '1|0|INCROOT 2|1|PUNCT',
                        '%mor': 'n|cracker .',
                        'MOT': 'cracker .'}

        :rtype: dict(int: dict(str: str))
        """
        return self._index_to_tiers

    def _get_index_to_tiers(self):
        result_with_collapses = {}
        index_ = -1  # utterance index (1st utterance is index 0)
        utterance = None

        for line in self.cha_lines():
            if line.startswith("@"):
                continue

            line_split = line.split()

            if line.startswith("*"):
                index_ += 1
                participant_code = line_split[0].lstrip("*").rstrip(":")
                utterance = " ".join(line_split[1:])
                result_with_collapses[index_] = {participant_code: utterance}

            elif utterance and line.startswith("%"):
                tier_marker = line_split[0].rstrip(":")
                result_with_collapses[index_][tier_marker] = " ".join(line_split[1:])

        # handle collapses such as [x 4]
        result_without_collapses = {}
        new_index = -1  # utterance index (1st utterance is index 0)
        collapse_pattern = re.compile(r"\[x \d+?\]")  # e.g., "[x <number(s)>]"
        number_regex = re.compile(r"\d+")

        for old_index in range(len(result_with_collapses)):
            tier_dict = result_with_collapses[old_index]
            participant_code = get_participant_code(tier_dict.keys())
            utterance = tier_dict[participant_code]

            try:
                collapse_str = collapse_pattern.search(utterance).group()
                collapse_number = int(number_regex.findall(collapse_str)[0])
            except (AttributeError, ValueError):
                collapse_number = 1

            for i in range(collapse_number):
                new_index += 1
                result_without_collapses[new_index] = tier_dict

        return result_without_collapses

    def headers(self):
        """
        Return the headers as a dict.

        :return: A dict of headers of the CHAT file.

        The keys are the header names
            as str (e.g., 'Begin', 'Participants', 'Date'). The header entry is
            the content for the respective header name.

        For the head 'Participants', the entry is a dict where the keys are the
            participant codes (e.g., 'CHI', 'MOT') and the value is a dict of
            information for the respective participant code. The keys of the
            information are as follows:

                * participant_label
                * language
                * corpus
                * code
                * age
                * sex
                * group
                * SES
                * role
                * education
                * custom

        :rtype: dict(str: dict)
        """
        return self._headers

    def _get_headers(self):
        headname_to_entry = {}

        for line in self.cha_lines():

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
                headname_to_entry["Participants"] = {}

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
                    headname_to_entry["Participants"][code] = {
                        "participant_name": participant_name
                    }

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
                    "SES",
                    "participant_role",
                    "education",
                    "custom",
                ]
                head_to_info = dict(zip(participant_info_heads, participant_info))

                headname_to_entry["Participants"][code].update(head_to_info)

            elif head == "Date":
                if "Date" not in headname_to_entry:
                    headname_to_entry["Date"] = []
                headname_to_entry["Date"].append(line)

            else:
                headname_to_entry[head] = line

        return headname_to_entry

    def participants(self):
        """
        Return the participant information as a dict.

        :return: A dict of participant information based on the @ID lines,
            where the key is the participant code, and the value is a dict of
            info for the participant. Example::

                {'CHI': {'SES': '',
                         'age': '1;6.',
                         'corpus': 'Brown',
                         'custom': '',
                         'education': '',
                         'group': '',
                         'language': 'eng',
                         'participant_label': 'Eve Target_Child',
                         'role': 'Target_Child',
                         'sex': 'female'},
                 'COL': {'SES': '',
                         'age': '',
                         'corpus': 'Brown',
                         'custom': '',
                         'education': '',
                         'group': '',
                         'language': 'eng',
                         'participant_label': 'Colin Investigator',
                         'role': 'Investigator',
                         'sex': ''},
                 'MOT': {'SES': '',
                         'age': '',
                         'corpus': 'Brown',
                         'custom': '',
                         'education': '',
                         'group': '',
                         'language': 'eng',
                         'participant_label': 'Sue Mother',
                         'role': 'Mother',
                         'sex': ''},
                 'RIC': {'SES': '',
                         'age': '',
                         'corpus': 'Brown',
                         'custom': '',
                         'education': '',
                         'group': '',
                         'language': 'eng',
                         'participant_label': 'Richard Investigator',
                         'role': 'Investigator',
                         'sex': ''}}
        """
        try:
            return self._headers["Participants"]
        except KeyError:
            return {}

    def participant_codes(self):
        """
        Return the set of participant codes (e.g., `{'CHI', 'MOT', 'FAT'}`).
        """
        try:
            return set(self._headers["Participants"].keys())
        except KeyError:
            return set()

    def languages(self):
        """
        Return the list of the languages involved based on the @Languages
        header.
        """
        languages_list = []

        try:
            languages_line = self._headers["Languages"]
        except KeyError:
            pass
        else:
            for language in languages_line.split(","):
                language = language.strip()
                if language:
                    languages_list.append(language)

        return languages_list

    def dates_of_recording(self):
        """
        Return the date of recording as a tuple of (*year*, *month*, *day*).
        If any errors arise (e.g., there's no date), return ``None``.

        :rtype: list(tuple(int, int, int))
        """
        try:
            dates = self._headers["Date"]
        except KeyError:
            return None

        return [convert_date_to_tuple(date) for date in dates]

    def date_of_birth(self):
        """
        Return the dates of birth as
        dict(participant code: (*year*, *month*, *day*)).
        If no date of birth is given for a participant,
        the value is ``None`` instead of the tuple.

        :rtype: dict(str: (int, int, int))
        """
        header_keys = self._headers.keys()
        participant_to_date = {}

        for header in header_keys:
            if not header.startswith("Birth of"):
                continue

            # e.g., header is 'Birth of CHI', participant is 'CHI'
            _, _, participant = header.split()
            date_str = self._headers[header]

            participant_to_date[participant] = convert_date_to_tuple(date_str)

        for participant in self.participants():
            if participant not in participant_to_date:
                participant_to_date[participant] = None

        return participant_to_date

    def age(self, participant="CHI", months=False):
        """
        Return the age of *participant* as a tuple or a float.

        :param participant: The participant specified, default to ``'CHI'``

        :param months: If True (default: False), return age in months.

        :return: The age as a 3-tuple of (years, months, days).
            If any errors arise (e.g., there's no age), ``None`` is returned.
            If *month* is True (default: False),
            return a float as age in months instead.

        :rtype: tuple or float
        """
        try:
            age_ = self._headers["Participants"][participant]["age"]

            year_str, _, month_day = age_.partition(";")
            month_str, _, day_str = month_day.partition(".")

            year_int = int(year_str) if year_str.isdigit() else 0
            month_int = int(month_str) if month_str.isdigit() else 0
            day_int = int(day_str) if day_str.isdigit() else 0

            if months:
                return year_int * 12 + month_int + day_int / 30
            else:
                return year_int, month_int, day_int
        except (KeyError, IndexError, ValueError):
            return None

    def utterances(self, participant=None, exclude=None, clean=True, time_marker=False):
        """
        Return a list of the utterances by *participant*
        as (*participant*, *utterance*) pairs.

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.

        :param clean: Whether to filter away the CHAT annotations in the
            utterance; default to ``True``.

        :param time_marker: Whether to include the timer marker in the
            utterance; default to ``False``. If ``True``, the list returned
            will be (*participant*, *utterance*, *timermarker*) pairs, where
            *timermarker* is a tuple with two integers for
            the start and end times (in milliseconds) for this utterance.
        """
        output = []
        participants = self._determine_participants(participant, exclude)

        for i in range(len(self)):
            tiermarker_to_line = self._index_to_tiers[i]

            for tier_marker in tiermarker_to_line.keys():
                if tier_marker in participants:
                    line = tiermarker_to_line[tier_marker]
                    if clean:
                        if time_marker:
                            try:
                                time_marker = get_time_marker(line)
                            except ValueError as e:
                                msg = (
                                    "At line %d in file %s: "
                                    % (
                                        i,
                                        self.filename(),
                                    )
                                    + str(e)
                                )
                                raise ValueError(msg)
                            output.append(
                                (
                                    tier_marker,
                                    clean_utterance(line),
                                    time_marker,
                                )
                            )
                        else:
                            output.append((tier_marker, clean_utterance(line)))
                    else:
                        output.append((tier_marker, line))
                    break
        return output

    def _determine_participants(self, participant, exclude):
        """Determine the target participants.

        Parameters
        ----------
        participant : str or iterable of str
            Participants to include.
            If unspecified or ``None``, all participant codes are included.
        exclude : str or iterable of str
            Participants to exclude.
            If unspecified or ``None``, no participant codes are excluded.

        Returns
        -------
        set of str
        """
        if participant is None and exclude is None:
            return self.participant_codes()

        if participant is None:
            include_participants = self.participant_codes()
        elif isinstance(participant, str):
            include_participants = {participant}
        elif hasattr(participant, "__iter__"):
            include_participants = set(participant)
        else:
            raise TypeError(
                '"participant" should be either str or '
                "an iterable of str: {}".format(repr(participant))
            )

        if exclude is None:
            exclude_participants = set()
        elif isinstance(exclude, str):
            exclude_participants = {exclude}
        elif hasattr(exclude, "__iter__"):
            exclude_participants = set(exclude)
        else:
            raise TypeError(
                '"exclude" should be either str or '
                "an iterable of str: {}".format(repr(exclude))
            )

        return {
            p
            for p in self.participant_codes()
            if p in include_participants and p not in exclude_participants
        }

    def words(self, participant=None, exclude=None):
        """
        Return a list of words by *participant*.

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.
        """
        return self._get_words(
            participant=participant, exclude=exclude, tagged=False, sents=False
        )

    def tagged_words(self, participant=None, exclude=None):
        """
        Return a list of tagged words by *participant*.

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.
        """
        return self._get_words(
            participant=participant, exclude=exclude, tagged=True, sents=False
        )

    def sents(self, participant=None, exclude=None):
        """
        Return a list of sents by *participant*.

        (utterances = sents in NLTK terminology)

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.
        """
        return self._get_words(
            participant=participant, exclude=exclude, tagged=False, sents=True
        )

    def tagged_sents(self, participant=None, exclude=None):
        """
        Return a list of tagged sents by *participant*.

        (utterances = sents in NLTK terminology)

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.
        """
        return self._get_words(
            participant=participant, exclude=exclude, tagged=True, sents=True
        )

    def _get_words(self, participant=None, exclude=None, tagged=True, sents=True):
        """
        Extract words for the specified participant(s).

        The representation of "word" depends on whether ``tagged`` is True, and
        is based to some extent on the NLTK conventions.

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.

        :param tagged:

        If ``tagged`` is True, a word is a 4-tuple of
            (*word*, *PoS*, *mor*, *gra*), where:

            * *word* is str
            * *PoS* is part-of-speech tag as str,
              forced to be in uppercase following NLTK
            * *mor* is morphological information as str
            * *gra* is grammatical relation, as a 3-tuple of
              (*self-position*, *head-position*, *relation*),
              with the data type (int, int, str).

        An example word with this representation::

        ('thought', 'V', 'think&PAST', (3, 0, 'ROOT'))

            where in the original data, "thought" is the transcription,
            %mor has "v|think&PAST", and %gra is "3|0|ROOT"

        This word representation is an extension of NLTK, where a tagged word
            is typically a 2-tuple of (word, PoS).

        If PoS, mor, gra correspond to a "word" that is a clitic (due to the
            tilde in the original CHAT data), then word is 'CLITIC'.

        If ``tagged`` is False, a word is simply the word (as a str) from the
            transcription. If the word is 'CLITIC", it is not included in the
            returned generator.

        :param sents: If ``sents`` (using NLTK terminology) is True,
            words from the same utterance (= "sentence") are grouped
            together into a list which is in turn yielded. Otherwise,
            individual words are directly yielded without utterance structure.
        """
        result_list = []
        participants = self._determine_participants(participant, exclude)

        if sents:
            add_function = lambda result_, sent_: result_.append(sent_)
        else:
            add_function = lambda result_, sent_: result_.extend(sent_)

        if tagged:
            sent_to_add = lambda sent_: sent_
        else:
            sent_to_add = lambda sent_: [x[0] for x in sent_ if x[0] != CLITIC]

        for participant_code, tagged_sent in self._all_tagged_sents:
            if participant_code not in participants:
                continue

            add_function(result_list, sent_to_add(tagged_sent))

        return result_list

    def _create_all_tagged_sents(self):
        result_list = []

        for i in range(self.number_of_utterances()):
            tiermarker_to_line = self._index_to_tiers[i]
            participant_code = get_participant_code(tiermarker_to_line.keys())

            # get the plain words from utterance tier
            utterance = clean_utterance(tiermarker_to_line[participant_code])
            words = utterance.split()

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

            if mor_items and ((len(words) + clitic_count) != len(mor_items)):
                message = (
                    "cannot align the utterance and %mor tiers:\n"
                    + "Filename: {}\nTiers --\n{}\n"
                    + "Cleaned-up utterance --\n{}"
                )
                raise ValueError(
                    message.format(
                        self.filename(), pformat(tiermarker_to_line), utterance
                    )
                )

            # %gra tier
            gra_items = []
            if "%gra" in tiermarker_to_line:
                for item in tiermarker_to_line["%gra"].split():
                    # an item is a string like '1|2|SUBJ'

                    item_list = []
                    for element in item.split("|"):
                        try:
                            converted_element = int(element)
                        except ValueError:
                            converted_element = element

                        item_list.append(converted_element)

                    gra_items.append(tuple(item_list))

            if mor_items and gra_items and (len(mor_items) != len(gra_items)):
                raise ValueError(
                    "cannot align the %mor and %gra tiers:\n{}".format(
                        pformat(tiermarker_to_line)
                    )
                )

            # utterance tier
            if mor_items and clitic_count:
                word_iterator = iter(words)
                utterance_items = [""] * len(mor_items)

                for j in range(len(mor_items)):
                    if j in clitic_indices:
                        utterance_items[j] = CLITIC
                    else:
                        utterance_items[j] = next(word_iterator)
            else:
                utterance_items = words

            # determine what to yield (and how) to create the generator
            if not mor_items:
                mor_items = [""] * len(utterance_items)
            if not gra_items:
                gra_items = [""] * len(utterance_items)

            sent = []

            for word, mor, gra in zip(utterance_items, mor_items, gra_items):
                pos, _, mor = mor.partition("|")

                output_word = (clean_word(word), pos.upper(), mor, gra)
                # pos in uppercase follows NLTK convention
                sent.append(output_word)

            result_list.append((participant_code, sent))

        return result_list

    def word_frequency(self, participant=None, exclude=None, keep_case=True):
        """
        Return the word frequency Counter dict for *participant*.

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.

        :param keep_case: If *keep_case* is True (the default), case
            distinctions are kept and word tokens like "the" and "The" are
            treated as distinct types. If *keep_case* is False, all case
            distinctions are collapsed, with all word tokens forced to be in
            lowercase.
        """
        output = Counter()

        if keep_case:
            for word in self.words(participant=participant, exclude=exclude):
                output[word] += 1
        else:
            for word in self.words(participant=participant, exclude=exclude):
                output[word.lower()] += 1

        return output

    def part_of_speech_tags(self, participant=None, exclude=None):
        """
        Return the set of part-of-speech tags in the data for *participant*.

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.
        """
        output_set = set()
        tagged_words = self.tagged_words(participant=participant, exclude=exclude)

        for tagged_word in tagged_words:
            pos = tagged_word[1]
            output_set.add(pos)

        return output_set

    def word_ngrams(self, n, participant=None, exclude=None, keep_case=True):
        """
        Return a Counter dict of *n*-grams (as an *n*-tuple of words)
        for *participant*.

        :param participant: The participant(s) of interest (default is all
            participants if unspecified). This parameter is flexible.
            Set it to be ``'CHI'`` for the target child only, for example.
            If multiple participants are desired, this parameter can take
            a sequence such as ``{'CHI', 'MOT'}`` to pick the participants in
            question. Underlyingly, this parameter actually performs
            regular expression matching
            (so passing ``'CHI'`` to this parameter is an
            exact match for the participant code ``'CHI'``, for instance).
            For child-directed speech (i.e., targeting all participant
            except ``'CHI'``), use ``^(?!.*CHI).*$``.

        :param keep_case: If *keep_case* is True (the default), case
            distinctions are kept and word tokens like "the" and "The" are
            treated as distinct types. If *keep_case* is False, all case
            distinctions are collapsed, with all word tokens forced to be in
            lowercase.
        """
        if (type(n) is not int) or (n < 1):
            raise ValueError("n must be a positive integer: %r" % n)

        if n == 1:
            return self.word_frequency(
                participant=participant, exclude=exclude, keep_case=keep_case
            )

        sents = self.sents(participant=participant, exclude=exclude)
        output_counter = Counter()

        for sent in sents:
            if len(sent) < n:
                continue
            if not keep_case:
                sent = [word.lower() for word in sent]
            ngram_list = zip(*[sent[i:] for i in range(n)])
            output_counter.update(ngram_list)

        return output_counter

    def MLU(self, participant="CHI", exclude=None):
        """
        Return the MLU in morphemes for *participant*
        (default to ``'CHI'``); same as ``MLUm()``.

        :param participant: The participant specified, default to ``'CHI'``
        """
        return get_MLUm(
            self.tagged_sents(participant=participant, exclude=exclude),
            pos_to_ignore=self.pos_to_ignore,
        )

    def MLUm(self, participant="CHI", exclude=None):
        """
        Return the MLU in morphemes for *participant*
        (default to ``'CHI'``); same as ``MLU()``.

        :param participant: The participant specified, default to ``'CHI'``
        """
        return get_MLUm(
            self.tagged_sents(participant=participant, exclude=exclude),
            pos_to_ignore=self.pos_to_ignore,
        )

    def MLUw(self, participant="CHI", exclude=None):
        """
        Return the mean length of utterance (MLU) in words for *participant*
        (default to ``'CHI'``).

        :param participant: The participant specified, default to ``'CHI'``
        """
        return get_MLUw(
            self.sents(participant=participant, exclude=exclude),
            words_to_ignore=self.words_to_ignore,
        )

    def TTR(self, participant="CHI", exclude=None):
        """
        Return the type-token ratio (TTR) for *participant*
        (default to ``'CHI'``).

        :param participant: The participant specified, default to ``'CHI'``
        """
        return get_TTR(
            self.word_frequency(participant=participant, exclude=exclude),
            words_to_ignore=self.words_to_ignore,
        )

    def IPSyn(self, participant="CHI", exclude=None):
        """
        Return the index of productive syntax (IPSyn) for *participant*
        (default to ``'CHI'``).

        :param participant: The participant specified, default to ``'CHI'``
        """
        return get_IPSyn(self.tagged_sents(participant=participant, exclude=exclude))

    def search(
        self,
        search_item,
        participant=None,
        exclude=None,
        match_entire_word=True,
        lemma=False,
        output_tagged=True,
        output_sents=True,
    ):
        return self._search(
            search_item,
            participant=participant,
            exclude=exclude,
            match_entire_word=match_entire_word,
            lemma=lemma,
            concordance=False,
            output_tagged=output_tagged,
            output_sents=output_sents,
        )

    def concordance(
        self,
        search_item,
        participant=None,
        exclude=None,
        match_entire_word=True,
        lemma=False,
    ):
        return self._search(
            search_item,
            participant=participant,
            exclude=exclude,
            match_entire_word=match_entire_word,
            lemma=lemma,
            concordance=True,
        )

    def _search(
        self,
        search_item,
        participant=None,
        exclude=None,
        match_entire_word=True,
        lemma=False,
        concordance=False,
        output_tagged=True,
        output_sents=True,
    ):
        taggedsent_charnumber_list = []
        # = list of (tagged_sent, char_number)

        # set up the match function
        if match_entire_word or lemma:
            match_function = lambda search_, test_: search_ == test_
        else:
            match_function = lambda search_, test_: search_ in test_

        tagged_sents = self.tagged_sents(participant=participant, exclude=exclude)

        for tagged_sent in tagged_sents:
            for i, tagged_word in enumerate(tagged_sent):
                word, pos, mor, rel = tagged_word

                # test_item targets word by default
                # if the "lemma" parameter is True,
                # then shift test_item to lemma extract from mor
                test_item = word
                if lemma:
                    test_item = get_lemma_from_mor(mor)

                # run the match test
                # if match, keep the tagged_sent and compute char_number
                # char_number = the number of characters that would precede the
                #               target **word** if sent was represented as str
                #               (as is the case when "concordance" is True)
                if match_function(search_item, test_item):

                    preceding_words = [tagged_sent[k][0] for k in range(i)]
                    preceding_words = [
                        w for w in preceding_words if w != CLITIC
                    ]  # remove CLITIC
                    char_number = (
                        sum(len(w) for w in preceding_words) + len(preceding_words) - 1
                    )  # plus spaces
                    taggedsent_charnumber_list.append((tagged_sent, char_number))

        if not taggedsent_charnumber_list:  # if empty
            return taggedsent_charnumber_list

        if not concordance:

            if output_sents:
                add_function = lambda result_, sent_: result_.append(sent_)
            else:
                add_function = lambda result_, sent_: result_.extend(sent_)

            if output_tagged:
                sent_to_add = lambda sent_: sent_
            else:
                sent_to_add = lambda sent_: [x[0] for x in sent_ if x[0] != CLITIC]

            result_list = []

            for tagged_sent, _ in taggedsent_charnumber_list:
                add_function(result_list, sent_to_add(tagged_sent))

            return result_list
        else:
            max_char_number = max([n for _, n in taggedsent_charnumber_list])
            result_list = []

            for tagged_sent, char_number in taggedsent_charnumber_list:
                sent = [word_ for word_, _, _, _ in tagged_sent if word_ != CLITIC]
                sent_str = " " * (max_char_number - char_number) + " ".join(sent)
                result_list.append(sent_str)

            return result_list
