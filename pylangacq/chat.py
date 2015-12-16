import os
import fnmatch

from pylangacq.util import *

# Tiers (excluding the utterances beginning with '*') that are of interest
TIER_MARKERS = {'%mor', '%gra'}


class Reader:
    """
    ``Reader`` is a class for reading multiple CHAT files. It is built on the
    ``SingleReader`` class.
    """
    def __init__(self, *filenames, tiers=TIER_MARKERS):
        """
        :param filenames: one or more filenames.

        A filename may match exactly a .cha file like
        ``eve01.cha`` or matches multiple files by glob patterns, e.g.,
        ``eve*.cha`` can match ``eve01.cha``, ``eve02.cha``, etc.
        Apart from ``*`` for any number (including zero) of characters,
        ``?`` is another commonly used wildcard and matches one character.

        The ``Reader`` class is set to find *unique* absolute-path filenames.
        This means that a call such as ``Reader('eve*.cha', '*01.cha')``
        (for all Eve files and all "01" files together) might seem to have
        overlapping or duplicate results (like ``eve01.cha`` which satisfies
        both ``eve*.cha`` and ``*01.cha``), but ``Reader`` filters away the
        duplicates.

        :return: ``self.filenames`` is a sorted list of matched absolute-path
        filenames.
        """
        self.tier_markers = tiers

        for filename in filenames:
            if type(filename) is not str:
                raise ValueError('{} is not str'.format(repr(filename)))
            if os.path.isabs(filename):
                raise ValueError('filename should not be an absolute path')

        abs_path = os.getcwd()

        # create filenames_current_dir to store all abs-path filenames
        #  in the current directory
        filenames_current_dir = [os.path.join(abs_path, fn)
                                 for fn in next(os.walk(abs_path))[2]]

        self.filenames = list()

        for filename in filenames:
            filename = os.path.normpath(os.path.join(abs_path, filename))
            self.filenames.extend(fnmatch.filter(filenames_current_dir,
                                                 filename))

        self.filenames = sorted(set(self.filenames))

    def number_of_files(self):
        """
        :return: the number of CHAT files
        :rtype: int
        """
        return len(self.filenames)

    def number_of_utterances(self):
        """
        :return: the total number of utterances across all CHAT files
        :rtype: int
        """
        return sum([SingleReader(filename,
                                 self.tier_markers).number_of_utterances()
                    for filename in self.filenames])

    def cha_lines(self):
        """
        Reads the files and cleans them up by undoing the line continuation
        with the tab character.

        :return: a dict where key is filename and value is
        a list iterator of all cleaned-up lines in the .cha file
        :rtype: dict(str: iter)
        """
        return {filename: SingleReader(filename, self.tier_markers).cha_lines()
                for filename in self.filenames}

    def tier_sniffer(self):
        """
        :return: a dict where key is filename and value is
        the information (as a dict(str: bool)) for whether a particular tier
        type (e.g., `%mor`) exists
        """
        return {filename: SingleReader(filename,
                                       self.tier_markers).tier_sniffer()
                for filename in self.filenames}

    def headers(self):
        """
        :return: a dict where key is filename and value is
        the headers (as a dict) of the CHAT file.
        :rtype: dict(str: dict)
        """
        return {filename: SingleReader(filename, self.tier_markers).headers
                for filename in self.filenames}

    def index_to_tiers(self):
        """
        :return: a dict where key is filename and value is
        the index_to_tiers dict of the CHAT file.
        :rtype: dict(str: dict)
        """
        return {filename: SingleReader(filename,
                                       self.tier_markers).index_to_tiers
                for filename in self.filenames}

    def participants(self):
        """
        :return: a dict where key is filename and value is
        participant information (as a dict) based on the @ID lines.
        :rtype: dict(str: dict)
        """
        return {filename: SingleReader(filename,
                                       self.tier_markers).participants()
                for filename in self.filenames}

    def participant_codes(self):
        """
        :return: a dict where key is filename and value is
        a set of the participant codes (e.g., `{'CHI', 'MOT', 'FAT'}`)
        :rtype: dict(str: set)
        """
        return {filename: SingleReader(filename,
                                       self.tier_markers).participant_codes()
                for filename in self.filenames}

    def languages(self):
        """
        :return: a dict where key is filename and value is
        a set of languages based on the @Languages headers
        :rtype: dict(str: set)
        """
        return {filename: SingleReader(filename, self.tier_markers).languages()
                for filename in self.filenames}

    def date(self):
        """
        Returns the date of recording.

        :return: a dict where key is filename and value is
        a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. Returns ``None`` instead
        of any errors arise (e.g., there's no date).
        :rtype: dict(str: tuple), where tuple could be None if no date
        """
        return {filename: SingleReader(filename, self.tier_markers).date()
                for filename in self.filenames}

    def age(self, participant='CHI'):
        """
        Returns the age of a particular participant.

        :param participant: an optional argument to specify which participant,
        default = ``'CHI'``
        :return: a dict where key is filename and value is
        a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. Returns ``None`` instead
        of any errors arise (e.g., there's no age).
        :rtype: dict(str: tuple or None)
        """
        return {filename: SingleReader(filename, self.tier_markers).age(
            participant=participant) for filename in self.filenames}

    def utterances(self, participant='**ALL**', clean=True):
        """
        Extracts participant-utterance pairs in order of how they appear in
        the transcript.

        :param participant:  which participant(s) are of interest, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.
        :param clean: whether to filter away the CHAT annotations in the
        utterance. Default to ``True``.
        :return: a dict of filenames to iterators of the
        (participant, utterance) tuples
        :rtype: dict(str: iter)
        """
        return {filename: SingleReader(filename, self.tier_markers).utterances(
            participant=participant, clean=clean)
                for filename in self.filenames}


class SingleReader:
    """
    ``SingleReader`` is a class for reading a single CHAT file.
    """
    def __init__(self, filename, tiers=TIER_MARKERS):
        """
        :param filename: absolute-path of a ``.cha`` file
        :return: ``self.filename`` is str
        """
        self.tier_markers = tiers

        if type(filename) is not str:
            raise ValueError('filename must be str')

        if os.path.isabs(filename):
            self.filename = filename
        else:
            abs_path = os.getcwd()
            self.filename = os.path.normpath(os.path.join(abs_path, filename))

        if not os.path.isfile(self.filename):
            raise FileNotFoundError(self.filename)

        self.headers = self._headers()
        self.index_to_tiers = self._index_to_tiers()

    def number_of_utterances(self):
        """
        :return: the number of utterances (lines starting with '*')
        :rtype: int
        """
        return len(self.index_to_tiers)

    def cha_lines(self):
        """
        Reads the .cha file and cleans it up by undoing the line continuation
        with the tab character.

        :return: a list iterator of all cleaned-up lines in the .cha file
        :rtype: iter
        """
        # In principle, either iterator or generator can serve our purposes
        # well. An iterator but not generator is chosen to be the returned
        # object, because we need access to the previous line just read in the
        # previous iteration in the for loop (in case when the present line
        # starts with a tab character).
        lines = list()

        for line in open(self.filename, 'rU'):
            if not line:
                continue

            line = line.rstrip()  # don't remove leading \t

            if line.startswith('\t'):
                previous_line = lines.pop()  # also removes it from "lines"
                line = '{} {}'.format(previous_line, line.strip())
                # removes leading/trailing characters (e.g. \t) from "line"

            lines.append(line)

        return iter(lines)

    def find_one_tier(self, lines, tier):
        """
        :param lines: an iterator of the CHAT file lines
        :param tier: tier name as str (e.g., `%mor`)
        :return: ``True`` or ``False``, for whether the tier exists in lines
        """
        present = False
        for line in lines:
            if line.startswith(tier):
                present = True
                break
        return present

    def tier_sniffer(self):
        """
        checks if the CHAT file contains the following tiers:

        - %mor
        - %gra

        :return: a dict where key is tier name (e.g., '%mor') and
        value is `True` or `False`
        :rtype: dict(str: bool)
        """
        sniffer_results = dict()

        for tier in self.tier_markers:
            sniffer_results[tier] = self.find_one_tier(self.cha_lines(), tier)

        return sniffer_results

    def _index_to_tiers(self):
        """
        Extracts in the CHAT file the utterances and tiers of interest.
        Each utterance is assigned an integer index (starting from 0).

        :return: a dict where key is utterance index and value is
        a dict, where key is tier marker and value is the list of items.
        Two key-value pairs in the output dict may look like this:

         1537: {'%gra': '1|2|MOD 2|0|INCROOT 3|2|PUNCT',
                '%mor': 'n|tapioca n|finger .',
                '*': 'tapioca finger . [+ IMIT]'},
         1538: {'%gra': '1|0|INCROOT 2|1|PUNCT',
                '%mor': 'n|cracker .',
                '*': 'cracker .'}

        :rtype: dict(int: dict(str: str))
        """
        result = dict()
        index_ = -1  # utterance index (1st utterance is index 0)
        utterance = None

        for line in self.cha_lines():
            if line.startswith('@'):
                continue

            line_split = line.split()
            tier_marker = startswithoneof(line, self.tier_markers)
            # tier_marker is '%mor', '%gra', or None

            if line.startswith('*'):
                index_ += 1
                participant_code = line_split[0].lstrip('*').rstrip(':')
                utterance_list = line_split[1:]
                utterance = ' '.join(utterance_list)
                result[index_] = {participant_code: utterance}
            elif utterance and tier_marker:
                result[index_][tier_marker] = ' '.join(line_split[1:])

        return result

    def _headers(self):
        """
        :return: a dict of headers of the .chat file.
        The keys are the header names
        as str (e.g., 'Begin', 'Participants', 'Date'). The header entry is
        the content for the respective header name.

        For the head 'Participants', the entry is a dict where the keys are the
        participant codes (e.g., 'CHI', 'MOT') and the value is a dict of
        information for the respective participant code. The keys of the
        information are as follows

        participant_label (from the '@Participants' field), language, corpus,
        code, age, sex, group, SES, role, education, custom
        :rtype: dict(str: dict)
        """
        headname_to_entry = dict()

        for line in self.cha_lines():

            if line.startswith('@Begin') or line.startswith('@End'):
                continue

            if not line.startswith('@'):
                continue

            # find head, e.g., "Languages", "Participants", "ID" etc
            head, _tab, line = line.partition('\t')
            line = line.strip()
            head = head.lstrip('@')  # remove beginning "@"
            head = head.rstrip(':')  # remove ending ":", if any

            if head == 'Participants':
                headname_to_entry['Participants'] = dict()

                participants = line.split(',')

                for participant in participants:
                    participant = participant.strip()
                    code, _space, participant_label = participant.partition(' ')
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
        :return: a dict of participant information based on the @ID lines.
        Key = participant code. Value = dict of info for the participant
        :rtype: dict
        """
        try:
            return self.headers['Participants']
        except KeyError:
            return dict()

    def participant_codes(self):
        """
        :return: a dict where key is filename and value is
        a set of the participant codes (e.g., `{'CHI', 'MOT', 'FAT'}`)
        :rtype: set
        """
        try:
            return set(self.headers['Participants'].keys())
        except KeyError:
            return set()

    def languages(self):
        """
        :return: a set of languages based on the @Languages headers
        :rtype: set
        """
        languages_set = set()

        try:
            languages_line = self.headers['Languages']
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
        Returns the date of recording.

        :return: a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. Returns ``None`` instead
        if any errors arise (e.g., there's no date).
        :rtype: tuple, or None if no date
        """
        try:
            date_str = self.headers['Date']
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
        Returns the age of a particular participant.

        :param participant: an optional argument to specify which participant,
        default = ``'CHI'``
        :return: a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. Returns ``None`` instead
        of any errors arise (e.g., there's no age).
        :rtype: tuple, or None
        """
        try:
            age_ = self.headers['Participants'][participant]['age']

            year, _semicolon, month_day = age_.partition(';')
            month, _period, day = month_day.partition('.')

            year = int(year) if year.isdigit() else 0
            month = int(month) if month.isdigit() else 0
            day = int(day) if day.isdigit() else 0
            return year, month, day
        except (KeyError, IndexError, ValueError):
            return None

    def utterances(self, participant='**ALL**', clean=True):
        """
        Extracts participant-utterance pairs in order of how they appear in
        the transcript.

        :param participant:  which participant(s) are of interest, default to
        ``'**ALL**'`` for all participants. Set it to be ``'CHI'`` for the
        target child, for example. For multiple participants, this parameter
        accepts a sequence of participants, such as ``{'CHI', 'MOT'}``.
        :param clean: whether to filter away the CHAT annotations in the
        utterance. Default to ``True``.
        :return: an iterator of the (participant, utterance) tuples
        :rtype: iter
        """
        if participant == '**ALL**':
            participants = self.participant_codes()
        elif type(participant) is str:
            participants = {participant}
        elif hasattr(participant, '__iter__'):
            participants = set(participant)
        else:
            raise TypeError('participant data type is invalid: {}'.format(
                repr(participant)))

        for i in range(self.number_of_utterances()):
            tiermarker_to_line = self.index_to_tiers[i]
            for tier_marker in tiermarker_to_line.keys():
                if tier_marker in participants:
                    line = tiermarker_to_line[tier_marker]
                    if clean:
                        yield tier_marker, self._clean_utterance(line)
                    else:
                        yield tier_marker, line
                    break

    def _clean_utterance(self, utterance):
        """
        Filters away unwanted CHAT-format material like corpus and conversation
        analysis-typed annotation in the input utterance.

        :param utterance: utterance as str
        :return: utterance without CHAT annotations
        :rtype: str
        """
        # Step 1:
        # If utterance has something like  "<aa bb cc> [x 5]" (repeated 5 times)
        # or "<aa bb cc> [?]" (uncertain transcription) and other similar cases
        # like overlapping, we need to keep "aa bb cc" as
        # actual transcription. Solution: Discard only the angle brackets.

        all_left_angle_bracket_indices = find_indices(utterance, '<')
        repeat_indices = find_indices(utterance, '> \[x')  # substring is '> [x'
        uncertain_indices = find_indices(utterance, '> \[\?')  # all regex here
        left_overlap_indices = find_indices(utterance, '> \[<')
        right_overlap_indices = find_indices(utterance, '> \[>')

        escape_left_angle_bracket_indices = list()
        check_indices = repeat_indices + uncertain_indices + \
            left_overlap_indices + right_overlap_indices

        for index_ in check_indices:
            for i in range(index_, -1, -1):
                if i in all_left_angle_bracket_indices:
                    escape_left_angle_bracket_indices.append(i)
                    break

        utterance_ = ''
        utterance = replace_all(utterance, {('> [x', '  [x'), ('> [?', '  [?'),
                                            ('> [>', '  [>'), ('> [<', '  [<')})
        for i, char in enumerate(utterance):
            if i not in escape_left_angle_bracket_indices:
                utterance_ += char

        # Step 2:
        # Remove things in a scope (by angle or square brackets). Examples:
        # from  'xx < aa bb > yy'  or  'xx [ aa bb ] yy'
        # to 'xx  yy' (2 spaces in the middle)

        utterance_ = re.sub('<[^<]+?>', '', utterance_)
        utterance_ = re.sub('\[[^/][^\[]+?\]', '', utterance_)

        # Step 3:
        # We need to escape the one item immediately preceding [/] or [//].
        # Solution: Replace ' [/' by '[/'.

        utterance_ = utterance_.replace(' [/', '[/')

        # Step 4:
        # Among the "words" in utterance_.split(), discard the unwanted ones.

        escape_words = {'(.)', '(..)', '(...)', 'xxx', '[/]', '[//]'}
        escape_prefixes = {'[', '<', '&'}
        escape_suffixes = {']', '>'}

        output_utterance_list = list()

        for word in utterance_.split():
            if (word not in escape_words) and \
                    (not startswithoneof(word, escape_prefixes)) and \
                    (not endswithoneof(word, escape_suffixes)):
                output_utterance_list.append(word)

        return ' '.join(output_utterance_list)
