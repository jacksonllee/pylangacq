import os
import fnmatch


class Reader:
    def __init__(self, *filenames):
        """
        :param filenames: a string that matches exactly a .cha file like
        ``eve01.cha`` or matches multiple files by glob patterns, e.g.,
        ``eve*.cha`` can match ``eve01.cha``, ``eve02.cha``, etc.
        Apart from ``*`` for any number (including zero) of characters,
        ``?`` is another commonly used wildcard and matches one character.

        :return: ``self.filenames`` is a list of matched absolute-path filenames
        """
        for filename in filenames:
            if type(filename) is not str:
                raise ValueError('{} is not str'.format(repr(filename)))
            if os.path.isabs(filename):
                raise ValueError('filename should not be an absolute path')

        abs_path = os.path.abspath('.')

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

    def cha_lines(self):
        """
        Reads the .cha file and cleans it up by undoing the line continuation
        with the tab character.

        :return: a dict where key is filename and value is
        a list iterator of all cleaned-up lines in the .cha file
        :rtype: dict(str: iter)
        """
        filename_to_lines = dict()

        for filename in self.filenames:
            lines = list()

            for line in open(filename, 'rU'):
                line = line.rstrip()  # don't remove leading \t

                if line.startswith('\t'):
                    previous_line = lines.pop()  # also removes it from "lines"
                    line = '{} {}'.format(previous_line, line.strip())
                    # removes leading/trailing characters (e.g. \t) from "line"

                lines.append(line)

            filename_to_lines[filename] = iter(lines)

        return filename_to_lines

    def headers(self):
        """
        :return: a dict where key is filename and value is
        a dict of headers of the .chat file.
        The keys are the label
        heads as str (e.g., 'Begin', 'Participants', 'Date'). The value are
        the respective content for the label head.

        For the head 'Participants', the value is a dict where the keys are the
        speaker codes (e.g., 'CHI', 'MOT') and the value is a list of
        information for the respective speaker code. The list of information is
        in this order:

        speaker label (from the '@Participants' field), language, corpus, code,
        age, sex, group, SES, role, education, custom
        :rtype: dict(str: dict)
        """
        filename_to_headers = dict()

        for filename in self.filenames:
            lines = self.cha_lines()[filename]
            headname_to_entry = dict()

            for line in lines:

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
                        code, _space, speaker_label = participant.partition(' ')
                        # code = speaker's code, e.g. CHI, MOT
                        headname_to_entry['Participants'][code] = \
                            {'speaker_label': speaker_label}

                elif head == 'ID':
                    speaker_info = line.split('|')[: -1]
                    # final empty str removed

                    code = speaker_info[2]
                    # speaker_info contains these in order:
                    #   language, corpus, code, age, sex, group, SES, role,
                    #   education, custom

                    del speaker_info[2]  # remove code info (3rd in list)
                    speaker_info_heads = ['language', 'corpus', 'age',
                                          'sex', 'group', 'SES', 'role',
                                          'education', 'custom']
                    head_to_info = {head: info
                                    for head, info in
                                    zip(speaker_info_heads, speaker_info)}

                    headname_to_entry['Participants'][code].update(head_to_info)

                else:
                    headname_to_entry[head] = line

            filename_to_headers[filename] = headname_to_entry

        return filename_to_headers

    def metadata(self):
        """
        :return: same as ``headers()``
        :rtype: dict(str: dict)
        """
        return self.headers()

    def participants(self):
        """
        :return: a dict where key is filename and value is
        a dict of participant information based on the @ID lines.
        Key = participant code. Value = dict of info for the participant
        :rtype: dict(str: dict)
        """
        filename_to_participants = dict()

        for filename in self.filenames:
            try:
                filename_to_participants[filename] = \
                    self.headers()[filename]['Participants']
            except KeyError:
                filename_to_participants[filename] = dict()

        return filename_to_participants

    def participant_codes(self):
        """
        :return: a dict where key is filename and value is
        a set of the speaker codes (e.g., `{'CHI', 'MOT', 'FAT'}`)
        :rtype: dict(str: set)
        """
        filename_to_participantcodes = dict()

        for filename in self.filenames:
            try:
                filename_to_participantcodes[filename] = \
                    set(self.headers()[filename]['Participants'].keys())
            except KeyError:
                filename_to_participantcodes[filename] = set()

        return filename_to_participantcodes

    def languages(self):
        """
        :return: a dict where key is filename and value is
        a set of languages based on the @Languages headers
        :rtype: dict(str: set)
        """
        filename_to_languages = dict()

        for filename in self.filenames:
            languages_set = set()

            try:
                languages_line = self.headers()[filename]['Languages']
            except KeyError:
                pass
            else:
                for language in languages_line.split(','):
                    language = language.strip()
                    if language:
                        languages_set.add(language)

            filename_to_languages[filename] = languages_set

        return filename_to_languages

    def date(self):
        """
        Returns the date of recording.

        :return: a dict where key is filename and value is
        a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. Returns ``None`` instead
        of any errors arise (e.g., there's no date).
        :rtype: dict(str: tuple), where tuple could be None if no date
        """
        filename_to_date = dict()

        for filename in self.filenames:
            try:
                date_str = self.headers()[filename]['Date']
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
                filename_to_date[filename] = (year, month, day)
            except (ValueError, KeyError):
                filename_to_date[filename] = None

        return filename_to_date

    def age(self, speaker='CHI'):
        """
        Returns the age of a particular speaker.

        :param speaker: an optional argument to specify which speaker,
        default = ``'CHI'``
        :return: a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. Returns ``None`` instead
        of any errors arise (e.g., there's no age).
        :rtype: tuple, or None
        """
        filename_to_age = dict()

        for filename in self.filenames:
            try:
                age_ = self.headers()[filename]['Participants'][speaker]['age']

                year, _semicolon, month_day = age_.partition(';')
                month, _period, day = month_day.partition('.')

                year = int(year) if year.isdigit() else 0
                month = int(month) if month.isdigit() else 0
                day = int(day) if day.isdigit() else 0
                filename_to_age[filename] = (year, month, day)
            except (KeyError, IndexError, ValueError):
                filename_to_age[filename] = None

        return filename_to_age
