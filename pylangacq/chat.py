import os
import fnmatch
from pprint import pformat
from collections import Counter
from itertools import chain

from pylangacq.util import *

ALL_PARTICIPANTS = '**ALL**'


class Reader:
    """
    A class for reading multiple CHAT files.
    """
    def __init__(self, *filenames):
        """
        :param filenames: One or more filenames. A filename may match exactly
        a CHAT file like ``eve01.cha`` or matches multiple files
        by glob patterns, e.g.,
        ``eve*.cha`` can match ``eve01.cha``, ``eve02.cha``, etc.
        Apart from ``*`` for any number (including zero) of characters,
        ``?`` is another commonly used wildcard and matches one character.
        A filename can be either an absolute or relative path.

        The ``Reader`` class is set to find *unique* absolute-path filenames.
        This means that a call such as ``Reader('eve*.cha', '*01.cha')``
        (for all Eve files and all "01" files together) might seem to have
        overlapping or duplicate results (like ``eve01.cha`` which satisfies
        both ``eve*.cha`` and ``*01.cha``), but ``Reader`` filters away the
        duplicates.
        """
        filenames_set = set()
        for filename in filenames:
            if type(filename) is not str:
                raise ValueError('{} is not str'.format(repr(filename)))

            abs_fullpath = os.path.abspath(filename)
            abs_dir = os.path.dirname(abs_fullpath)

            if not os.path.isdir(abs_dir):
                raise ValueError('dir does not exist: {}'.format(abs_dir))

            candidate_filenames = [os.path.join(abs_dir, fn)
                                   for fn in next(os.walk(abs_dir))[2]]

            filenames_set.update(fnmatch.filter(candidate_filenames,
                                                abs_fullpath))

        self._filenames = filenames_set

    def __len__(self):
        """
        Return the number of files.

        :return: The number of files

        :rtype: int
        """
        return len(self._filenames)

    def filenames(self):
        """
        Return the set of absolute-path filenames.

        :return: The set of absolute-path filenames.
        """
        return self._filenames

    def number_of_files(self):
        """
        Return the number of files.

        :return: The number of files

        :rtype: int
        """
        return self.__len__()

    def number_of_utterances(self):
        """
        Return a dict mapping a filename to the file's number of utterances.

        :return: A dict where key is filename and value is
        the file's number of utterances

        :rtype: dict(str: int)
        """
        return {filename: SingleReader(filename).number_of_utterances()
                for filename in self._filenames}

    def total_number_of_utterances(self):
        """
        Return the total number of utterances.

        :return: The total number of utterances across all CHAT files

        :rtype: int
        """
        return sum([SingleReader(filename).number_of_utterances()
                    for filename in self._filenames])

    def headers(self):
        """
        Return a dict mapping a filename to the headers.

        :return: A dict where key is filename and value is
        the headers (as a dict) of the CHAT file.

        :rtype: dict(str: dict)
        """
        return {filename: SingleReader(filename).headers()
                for filename in self._filenames}

    def index_to_tiers(self):
        """
        Return a dict mapping a filename to the file's index_to_tiers dict.

        :return: A dict where key is filename and value is
        the index_to_tiers dict of the CHAT file.

        :rtype: dict(str: dict)
        """
        return {filename: SingleReader(filename).index_to_tiers()
                for filename in self._filenames}

    def participants(self):
        """
        Return a dict mapping a filename to the file's participant info dict.

        :return: A dict where key is filename and value is
        participant information as a dict.

        :rtype: dict(str: dict)
        """
        return {filename: SingleReader(filename).participants()
                for filename in self._filenames}

    def participant_codes(self):
        """
        Return a dict mapping a filename to the file's set of participant codes.

        :return: A dict where key is filename and value is
        a set of the participant codes (e.g., ``{'CHI', 'MOT', 'FAT'}``)

        :rtype: dict(str: set)
        """
        return {filename: SingleReader(filename).participant_codes()
                for filename in self._filenames}

    def languages(self):
        """
        Return a dict mapping a filename to the set of languages used.

        :return: A dict where key is filename and value is
        a set of languages based on the @Languages headers

        :rtype: dict(str: set)
        """
        return {filename: SingleReader(filename).languages()
                for filename in self._filenames}

    def date(self):
        """
        Return a dict mapping a filename to the date.

        :return: A dict where key is filename and value is
        a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``.
        The value is ``None`` instead if any errors arise
        (e.g., there's no date).

        :rtype: dict(str: tuple), where tuple could be None if no date
        """
        return {filename: SingleReader(filename).date()
                for filename in self._filenames}

    def age(self, participant='CHI'):
        """
        Return a dict mapping a filename to the age of the *participant*.

        :param participant: The specified participant, default to ``'CHI'``

        :return: A dict where key is filename and value is
        a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``.
        The value is ``None`` instead if any errors arise
        (e.g., there's no age).

        :rtype: dict(str: tuple), where tuple could be None if no age
        """
        return {filename: SingleReader(filename).age(
            participant=participant) for filename in self._filenames}

    def utterances(self, participant=ALL_PARTICIPANTS, clean=True):
        """
        Return a dict mapping a filename to the file's
        (*participant*, *utterance*) pairs.

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :param clean: Whether to filter away the CHAT annotations in the
        utterance, default to ``True``.

        :return: A dict where key is filename and value is
        an iterator of the (*participant*, *utterance*) tuples

        :rtype: dict(str: iter)
        """
        return {filename: SingleReader(filename).utterances(
            participant=participant, clean=clean)
                for filename in self._filenames}

    def word_frequency(self, participant='CHI', keep_case=True):
        """
        Return a dict mapping a filename to the file's word frequency dict
        for the specified *participant*.

        :param participant: The specified participant, default to ``'CHI'``

        :return: A dict where key is filename and value is
        a Counter dict of word-frequency pairs.

        :rtype: dict(str: Counter)
        """
        return {filename: SingleReader(filename).word_frequency(
            participant=participant, keep_case=keep_case)
                for filename in self._filenames}

    def words(self, participant=ALL_PARTICIPANTS):
        """
        Return a dict mapping a filename to the file's generator of words
        for the specified *participant*.

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :return: A dict where key is filename and value is
        a generator of words

        :rtype: dict(str: generator)
        """
        return {filename: SingleReader(filename).words(
            participant=participant) for filename in self._filenames}

    def tagged_words(self, participant=ALL_PARTICIPANTS):
        """
        Return a dict mapping a filename to the file's generator of tagged words
        for the specified *participant*.

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :return: A dict where key is filename and value is
        a generator of tagged words

        :rtype: dict(str: generator)
        """
        return {filename: SingleReader(filename).tagged_words(
            participant=participant) for filename in self._filenames}

    def sents(self, participant=ALL_PARTICIPANTS):
        """
        Return a dict mapping a filename to the file's generator of sents
        for the specified *participant*

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :return: A dict where key is filename and value is
        a generator of sents

        :rtype: dict(str: generator)
        """
        return {filename: SingleReader(filename).sents(
            participant=participant) for filename in self._filenames}

    def tagged_sents(self, participant=ALL_PARTICIPANTS):
        """
        Return a dict mapping a filename to the file's generator of tagged sents
        for the specified *participant*

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :return: A dict where key is filename and value is
        a generator of tagged sents

        :rtype: dict(str: generator)
        """
        return {filename: SingleReader(filename).tagged_sents(
            participant=participant) for filename in self._filenames}

    def all_words(self, participant=ALL_PARTICIPANTS):
        """
        Return a generator of words for *participant* in all files.

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :return: a generator of words (as an itertools chain)
        """
        return chain(*(SingleReader(filename).words(participant=participant)
                       for filename in sorted(self._filenames)))

    def all_tagged_words(self, participant=ALL_PARTICIPANTS):
        """
        Return a generator of tagged words for *participant* in all files.

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :return: a generator of tagged words (as an itertools chain)
        """
        return chain(*(SingleReader(filename).tagged_words(
            participant=participant) for filename in sorted(self._filenames)))

    def all_sents(self, participant=ALL_PARTICIPANTS):
        """
        Return a generator of sents for *participant* in all files.

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :return: a generator of sents (as an itertools chain)
        """
        return chain(*(SingleReader(filename).sents(participant=participant)
                       for filename in sorted(self._filenames)))

    def all_tagged_sents(self, participant=ALL_PARTICIPANTS):
        """
        Return a generator of tagged sents for *participant* in all files.

        :param participant:  The participant(s) being specified, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :return: a generator of tagged sents (as an itertools chain)
        """
        return chain(*(SingleReader(filename).tagged_sents(
            participant=participant) for filename in sorted(self._filenames)))


class SingleReader:
    """
    A class for reading a single CHAT file.
    """
    def __init__(self, filename):
        """
        :param filename: The absolute path of the CHAT file
        """
        if type(filename) is not str:
            raise ValueError('filename must be str')

        self._filename = os.path.abspath(filename)

        if not os.path.isfile(self._filename):
            raise FileNotFoundError(self._filename)

        self._headers = self._get_headers()
        self._index_to_tiers = self._get_index_to_tiers()
        self.tier_markers = self._tier_markers()

    def __len__(self):
        """
        Return the number of utterances.

        :return: The number of utterances (lines starting with '*')

        :rtype: int
        """
        return len(self._index_to_tiers)

    def number_of_utterances(self):
        """
        Return the number of utterances.

        :return: The number of utterances (lines starting with '*')

        :rtype: int
        """
        return self.__len__()

    def filename(self):
        """
        Return the filename.

        :return: The filename.

        :rtype: str
        """
        return self._filename

    def cha_lines(self):
        """
        Read the CHAT file and undo the line continuations by tab.

        :return: A generator of all cleaned-up lines in the CHAT file

        :rtype: generator
        """
        previous_line = ''

        for line in open(self._filename, 'rU'):
            current_line = line.rstrip()  # don't remove leading \t

            if not current_line:
                continue

            if previous_line and current_line.startswith('\t'):
                previous_line = '{} {}'.format(previous_line,
                                               current_line.strip())  # strip \t
            elif previous_line:
                yield previous_line
                previous_line = current_line
            else:  # when it's the very first line
                previous_line = current_line
        yield previous_line  # don't forget the very last line!

    def _tier_markers(self):
        """
        Determine what the %-tiers are.

        :return: The set of %-beginning tier markers used in the CHAT file

        :rtype: set
        """
        result = set()
        for tiermarkers_to_tiers in self._index_to_tiers.values():
            for tier_marker in tiermarkers_to_tiers.keys():
                if tier_marker.startswith('%'):
                    result.add(tier_marker)
        return result

    def index_to_tiers(self):
        """
        Extract and organize the utterances and the corresponding tiers.

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
        result = dict()
        index_ = -1  # utterance index (1st utterance is index 0)
        utterance = None

        for line in self.cha_lines():
            if line.startswith('@'):
                continue

            line_split = line.split()

            if line.startswith('*'):
                index_ += 1
                participant_code = line_split[0].lstrip('*').rstrip(':')
                utterance = ' '.join(line_split[1:])
                result[index_] = {participant_code: utterance}
            elif utterance and line.startswith('%'):
                tier_marker = line_split[0].rstrip(':')
                result[index_][tier_marker] = ' '.join(line_split[1:])

        return result

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
        headname_to_entry = dict()

        for line in self.cha_lines():

            if line.startswith('@Begin') or line.startswith('@End'):
                continue

            if not line.startswith('@'):
                continue

            # find head, e.g., "Languages", "Participants", "ID" etc
            head, _, line = line.partition('\t')
            line = line.strip()
            head = head.lstrip('@')  # remove beginning "@"
            head = head.rstrip(':')  # remove ending ":", if any

            if head == 'Participants':
                headname_to_entry['Participants'] = dict()

                participants = line.split(',')

                for participant in participants:
                    participant = participant.strip()
                    code, _, participant_label = participant.partition(' ')
                    # code = participant code, e.g. CHI, MOT
                    headname_to_entry['Participants'][code] = \
                        {'participant_label': participant_label}

            elif head == 'ID':
                participant_info = line.split('|')[: -1]
                # final empty str removed

                code = participant_info[2]
                # participant_info contains these in order:
                #   language, corpus, code, age, sex, group, SES, role,
                #   education, custom

                del participant_info[2]  # remove code info (3rd in list)
                participant_info_heads = ['language', 'corpus', 'age', 'sex',
                                          'group', 'SES', 'role',
                                          'education', 'custom']
                head_to_info = {head: info
                                for head, info in
                                zip(participant_info_heads, participant_info)}

                headname_to_entry['Participants'][code].update(head_to_info)

            else:
                headname_to_entry[head] = line

        return headname_to_entry

    def participants(self):
        """
        Return the participant information as a dict.

        :return: A dict of participant information based on the @ID lines,
        where the key is the participant code, and the value is a dict of info
        for the participant. Example::

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

        :rtype: dict
        """
        try:
            return self._headers['Participants']
        except KeyError:
            return dict()

    def participant_codes(self):
        """
        Return the participant codes as a set.

        :return: A dict where key is filename and value is
        a set of the participant codes (e.g., `{'CHI', 'MOT', 'FAT'}`)

        :rtype: set
        """
        try:
            return set(self._headers['Participants'].keys())
        except KeyError:
            return set()

    def languages(self):
        """
        Return as a set the languages of the CHAT transcript.

        :return: The set of languages based on the @Languages headers

        :rtype: set
        """
        languages_set = set()

        try:
            languages_line = self._headers['Languages']
        except KeyError:
            pass
        else:
            for language in languages_line.split(','):
                language = language.strip()
                if language:
                    languages_set.add(language)

        return languages_set

    def date(self):
        """
        Return the date of recording as a tuple.

        :return: The date of recording as a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. If any errors arise
        (e.g., there's no date), ``None`` is returned.

        :rtype: tuple, or None if no valid date
        """
        try:
            date_str = self._headers['Date']
            day_str, month_str, year_str = date_str.split('-')
            day = int(day_str)
            year = int(year_str)

            month_to_int = {
                'JAN': 1,
                'FEB': 2,
                'MAR': 3,
                'APR': 4,
                'MAY': 5,
                'JUN': 6,
                'JUL': 7,
                'AUG': 8,
                'SEP': 9,
                'OCT': 10,
                'NOV': 11,
                'DEC': 12,
            }

            month = month_to_int[month_str]
            return year, month, day
        except (ValueError, KeyError):
            return None

    def age(self, participant='CHI'):
        """
        Return the age of *participant* as a tuple.

        :param participant: The participant specified, default to ``'CHI'``

        :return: The age as a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. If any errors arise
        (e.g., there's no age), ``None`` is returned.

        :rtype: tuple, or None
        """
        try:
            age_ = self._headers['Participants'][participant]['age']

            year, _, month_day = age_.partition(';')
            month, _, day = month_day.partition('.')

            year = int(year) if year.isdigit() else 0
            month = int(month) if month.isdigit() else 0
            day = int(day) if day.isdigit() else 0
            return year, month, day
        except (KeyError, IndexError, ValueError):
            return None

    def utterances(self, participant=ALL_PARTICIPANTS, clean=True):
        """
        Return the utterances by *participant*
        as (*participant*, *utterance*) pairs.

        :param participant: Participant(s) of interest, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

        :param clean: Whether to filter away the CHAT annotations in the
        utterance; default to ``True``.

        :return: A generator of the (participant, utterance) tuples
        in the order of how the utterances appear in the transcript.

        :rtype: generator
        """
        # TODO: collapses like [x 4] not yet handled
        participants = self._determine_participants(participant)

        for i in range(self.number_of_utterances()):
            tiermarker_to_line = self._index_to_tiers[i]

            for tier_marker in tiermarker_to_line.keys():
                if tier_marker in participants:
                    line = tiermarker_to_line[tier_marker]
                    if clean:
                        yield tier_marker, clean_utterance(line)
                    else:
                        yield tier_marker, line
                    break

    def _determine_participants(self, participant):
        """
        Determine the target participants.

        :param participant: Participant as str,
        or a sequence of participants

        :return: a set of participants of interest

        :rtype: set
        """
        if participant == ALL_PARTICIPANTS:
            participants = self.participant_codes()
        elif type(participant) is str:
            participants = {participant}
        elif hasattr(participant, '__iter__'):
            participants = set(participant)
        else:
            raise TypeError('participant data type is invalid: {}'.format(
                repr(participant)))
        return participants

    def words(self, participant=ALL_PARTICIPANTS):
        """
        Return a generator of words by *participant*.

        :param participant: Participant(s) of interest, as a str (e.g., 'CHI')
        for one participant or as a sequence of str for multiple ones.

        :return: generator of words
        """
        return self._get_words(participant=participant,
                               tagged=False, sents=False)

    def tagged_words(self, participant=ALL_PARTICIPANTS):
        """
        Return a generator of  tagged words by *participant*.

        :param participant: Participant(s) of interest, as a str (e.g., 'CHI')
        for one participant or as a sequence of str for multiple ones.

        :return: generator of tagged words
        """
        return self._get_words(participant=participant,
                               tagged=True, sents=False)

    def sents(self, participant=ALL_PARTICIPANTS):
        """
        Return a generator of sents by *participant*.

        (utterances = sents in NLTK terminology)

        :param participant: Participant(s) of interest, as a str (e.g., 'CHI')
        for one participant or as a sequence of str for multiple ones.

        :return: generator of sents.
        """
        return self._get_words(participant=participant,
                               tagged=False, sents=True)

    def tagged_sents(self, participant=ALL_PARTICIPANTS):
        """
        Return a generator of tagged sents by *participant*.

        (utterances = sents in NLTK terminology)

        :param participant: Participant(s) of interest, as a str (e.g., 'CHI')
        for one participant or as a sequence of str for multiple ones.

        :return: generator of tagged sents.
        """
        return self._get_words(participant=participant,
                               tagged=True, sents=True)

    def _get_words(self, participant=ALL_PARTICIPANTS, tagged=True, sents=True):
        """
        Extract words for the specified participant(s).

        The representation of "word" depends on whether ``tagged`` is True, and
        is based to some extent on the NLTK conventions.

        :param participant:  Participant(s) of interest, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.

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

        This word representation is an extension of NLTK, where a tagged word is
        typically a 2-tuple of (word, PoS).

        If PoS, mor, gra correspond to a "word" that is a clitic (due to the
        tilde in the original CHAT data), then word is 'CLITIC'.

        If ``tagged`` is False, a word is simply the word (as a str) from the
        transcription. If the word is 'CLITIC", it is not included in the
        returned generator.

        :param sents: If ``sents`` (using NLTK terminology) is True,
        words from the same utterance (= "sentence") are grouped
        together into a list which is in turn yielded. Otherwise, individual
        words are directly yielded without utterance structure.

        :return: A generator of either sents of words, or just words
        """
        # TODO: collapses like [x 4] not yet handled
        participants = self._determine_participants(participant)

        for i in range(self.number_of_utterances()):
            tiermarker_to_line = self._index_to_tiers[i]
            participant_code = get_participant_code(tiermarker_to_line.keys())

            if participant_code not in participants:
                continue

            # get the plain words from utterance tier
            utterance = clean_utterance(tiermarker_to_line[participant_code])
            words = utterance.split()

            # %mor tier
            clitic_indices = list()  # indices at the word items
            clitic_count = 0

            mor_items = list()
            if '%mor' in tiermarker_to_line:
                mor_split = tiermarker_to_line['%mor'].split()

                for j, item in enumerate(mor_split):
                    tilde_count = item.count('~')

                    if tilde_count:
                        item_split = item.split('~')

                        for k in range(tilde_count):
                            clitic_indices.append(clitic_count + j + k + 1)
                            clitic_count += 1

                            mor_items.append(item_split[k])

                        mor_items.append(item_split[-1])
                    else:
                        mor_items.append(item)

            if mor_items and \
                    ((len(words) + clitic_count) != len(mor_items)):
                raise ValueError(
                    'cannot align the utterance and %mor tiers:\n{}'.format(
                        pformat(tiermarker_to_line)))

            # %gra tier
            gra_items = list()
            if '%gra' in tiermarker_to_line:
                for item in tiermarker_to_line['%gra'].split():
                    # an item is a string like '1|2|SUBJ'

                    item_list = list()
                    for element in item.split('|'):
                        try:
                            converted_element = int(element)
                        except ValueError:
                            converted_element = element

                        item_list.append(converted_element)

                    gra_items.append(tuple(item_list))

            if mor_items and gra_items and \
                    (len(mor_items) != len(gra_items)):
                raise ValueError(
                    'cannot align the %mor and %gra tiers:\n{}'.format(
                        pformat(tiermarker_to_line)))

            # utterance tier
            if mor_items and clitic_count:
                word_iterator = iter(words)
                utterance_items = [''] * len(mor_items)

                for j in range(len(mor_items)):
                    if j in clitic_indices:
                        utterance_items[j] = CLITIC
                    else:
                        utterance_items[j] = next(word_iterator)
            else:
                utterance_items = words

            # determine what to yield (and how) to create the generator
            if not mor_items:
                mor_items = [''] * len(utterance_items)
            if not gra_items:
                gra_items = [''] * len(utterance_items)

            if sents:
                sent = list()

            for word, mor, gra in zip(utterance_items, mor_items, gra_items):
                pos, _, mor = mor.partition('|')

                if tagged:
                    output_word = (word, pos.upper(), mor, gra)
                    # pos in uppercase follows NLTK convention
                elif word == CLITIC:
                    # if tagged is False and word is the clitic
                    continue
                else:
                    output_word = word

                if sents:
                    sent.append(output_word)
                else:
                    yield output_word

            if sents:
                yield sent

    def word_frequency(self, participant=ALL_PARTICIPANTS, keep_case=True):
        """
        Return word frequency information for the specified *participant*.

        :param keep_case: If *keep_case* is True (the default), case
        distinctions are kept and word tokens like "the" and "The" are treated
        as distinct types. If *keep_case* is False, all case distinctions are
        collapsed, with all word tokens forced to be in lowercase.

        :return: a Counter dict of word-frequency pairs

        :rtype: Counter
        """
        # TODO: collapses like [x 4] not yet handled
        output = Counter()

        if keep_case:
            for word in self.words(participant=participant):
                output[word] += 1
        else:
            for word in self.words(participant=participant):
                output[word.lower()] += 1

        return output


def clean_utterance(utterance):
    """
    Filter away the CHAT-style annotations in *utterance*.

    :param utterance: The utterance as a str

    :return: The utterance without CHAT annotations

    :rtype: str
    """
    # Function tested with the Brown portion (Adam, Eve, and Sarah) of CHILDES

    # *** At the end of each step, apply remove_extra_spaces(). ***

    # Step 1: Remove unwanted scope elements (only the very certain cases), e.g.
    # [= whatever] for explanations
    # [x how_many_times] for collapses
    # [+ whatever] for actions etc
    # [* whatever] for error coding
    # [=? whatever] for uncertain transcriptions
    # [=! whatever] for actions etc
    # [% whatever] for random noises?
    # [?] for best guess

    utterance = re.sub('\[= [^\[]+?\]', '', utterance)
    utterance = re.sub('\[x \d+?\]', '', utterance)
    utterance = re.sub('\[\+ [^\[]+?\]', '', utterance)
    utterance = re.sub('\[\* [^\[]+?\]', '', utterance)
    utterance = re.sub('\[=\? [^\[]+?\]', '', utterance)
    utterance = re.sub('\[=! [^\[]+?\]', '', utterance)
    utterance = re.sub('\[% [^\[]+?\]', '', utterance)
    utterance = utterance.replace('[?]', '')
    utterance = remove_extra_spaces(utterance)
    # print('step 1:', utterance)

    # Step 2: Pad elements with spaces to avoid human transcription errors etc
    # If utterance has these delimiters: [ ]
    # then pad them with extra spaces to avoid errors in transcriptions
    # like "movement[?]" (--> "movement [?]")
    #
    # If utterance has:
    #     “ (beginning quote)
    #     ” (ending quote)
    #     , (comma)
    #     ? (question mark)
    #     . (period)
    # then pad them with extra spaces.

    utterance = utterance.replace('[', ' [')
    utterance = utterance.replace(']', '] ')
    utterance = utterance.replace('“', ' “ ')
    utterance = utterance.replace('”', ' ” ')
    utterance = re.sub('[^\+],', ' , ', utterance)
    utterance = re.sub('[^\[]\?', ' ? ', utterance)
    # utterance = re.sub('[^\(\[\.\+]\.', ' . ', utterance)
    utterance = remove_extra_spaces(utterance)
    # print('step 2:', utterance)

    # Step 3: Handle 'xx [zz]' or '<xx yy> [zz]'
    #
    # Three cases:
    # 1) Keep 'xx' and discard 'zz'. Examples:
    #        [x how_many_times]
    #        [?] for uncertain transcriptions
    #        [<] and [>] for overlapping
    #
    # 2) Discard 'xx' and keep 'zz'. Examples:
    #        [:: something] or [: something] for errors
    #
    # 3) Discard 'xx' (no 'zz'). Examples:
    #        [/] and [//] for repetitions

    discard_signal_indices = set()
    discard_signal_indices.update(find_indices(utterance, '\[:'),
                                  find_indices(utterance, '\[/'))  # use regex

    discard_end_indices = [i-2 for i in sorted(discard_signal_indices)]
    discard_start_indices = list()
    for end_index in discard_end_indices:
        if utterance[end_index] == '>':
            for i in range(end_index, -1, -1):
                if utterance[i] == '<' and utterance[i + 1] != ']':
                    discard_start_indices.append(i)
                    break
        else:
            for i in range(end_index, -1, -1):
                if i == 0:
                    discard_start_indices.append(0)
                    break
                elif utterance[i] == ' ':
                    discard_start_indices.append(i + 1)
                    break

    new_utterance = ''
    for i in range(len(utterance)):
        ignore_this_character = False
        for start_i, end_i in zip(discard_start_indices, discard_end_indices):
            if (i >= start_i) and (i <= end_i):
                ignore_this_character = True
                break
        if not ignore_this_character:
            new_utterance += utterance[i]

    utterance = remove_extra_spaces(new_utterance)
    # print('step 3:', utterance)

    # Step 4: Remove unwanted elements (only the very certain cases).

    unwanted_elements = {'(.)', '(..)', '(...)',
                         'xxx', 'www', 'yyy',
                         # '+"', '+.',
                         }
    for unwanted_element in unwanted_elements:
        utterance = utterance.replace(unwanted_element, '')
    utterance = remove_extra_spaces(utterance)
    # print('step 4:', utterance)

    # Step 5: Split utterance by spaces and determine whether to keep items.

    escape_prefixes = {'[?', '[/', '[<', '[>', '[:', '[!', '[*',
                       '+"', '+,', '&'}
    escape_words = {'0'}
    keep_prefixes = {'+"/', '+,/'}

    words = utterance.split()
    new_words = list()

    for word in words:
        word = re.sub('\A<', '', word)  # remove beginning <
        word = re.sub('>\Z', '', word)  # remove final >

        if bool(re.compile('[^\]]+?\]\Z').match(word)):
            # word ends with ]
            word = word[: -1]

        if startswithoneof(word, keep_prefixes) or \
                ((word not in escape_words) and \
                (not startswithoneof(word, escape_prefixes))):
            new_words.append(word)

    # print('step 5:', remove_extra_spaces(' '.join(new_words)))

    return remove_extra_spaces(' '.join(new_words))


def get_participant_code(tier_marker_seq):
    """
    Return the participant code from a tier marker set.

    :param tier_marker_seq: A sequence of tier markers like
    ``{'CHI', '%mor', '%gra'}``

    :return: A participant code, e.g., ``'CHI'``

    :rtype: str, or None if no participant code is found
    """
    for tier_marker in tier_marker_seq:
        if not tier_marker.startswith('%'):
            return tier_marker
    return None
