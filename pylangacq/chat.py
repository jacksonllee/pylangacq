
class Reader:

    def __init__(self, filename):
        self.filename = filename

    def cha_lines(self):
        """
        Reads the .cha file and cleans it up by undoing the line continuation
        with the tab character.

        :return: a list iterator of all cleaned-up lines in the .cha file
        :rtype: iter
        """
        lines = list()

        for line in open(self.filename, 'rU'):
            line = line.rstrip()  # don't remove leading \t

            if line.startswith('\t'):
                previous_line = lines.pop()  # also removes it from "lines"
                line = '{} {}'.format(previous_line, line.strip())
                # removes leading/trailing characters (e.g. \t) from "line"

            lines.append(line)

        return iter(lines)

    def metadata(self):
        """
        :return: a ``dict`` of metadata of the .chat file.
        The keys are the label
        heads as str (e.g., 'Begin', 'Participants', 'Date'). The value are
        the respective content for the label head.

        For the head 'Participants', the value is a dict where the keys are the
        speaker codes (e.g., 'CHI', 'MOT') and the value is a list of
        information for the respective speaker code. The list of information is
        in this order:

        speaker label (from the '@Participants' field), language, corpus, code,
        age, sex, group, SES, role, education, custom
        :rtype: dict
        """
        outdict = dict()

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
                outdict['Participants'] = dict()

                participants = line.split(',')

                for participant in participants:
                    participant = participant.strip()
                    code, _space, speaker_label = participant.partition(' ')
                    # code = speaker's code, e.g. CHI, MOT
                    outdict['Participants'][code] = \
                        {'speaker_label': speaker_label}

            elif head == 'ID':
                speaker_info = line.split('|')[: -1]  # final empty str removed
                code = speaker_info[2]
                # speaker_info contains these in order:
                #   language, corpus, code, age, sex, group, SES, role,
                #   education, custom

                del speaker_info[2]  # remove code info (3rd in list)
                speaker_info_heads = ['language', 'corpus', 'age',
                    'sex', 'group', 'SES', 'role', 'education', 'custom']
                speaker_info_dict = {head: info
                    for head, info in zip(speaker_info_heads, speaker_info)}

                outdict['Participants'][code].update(speaker_info_dict)

            else:
                outdict[head] = line

        return outdict

    def participants(self):
        """
        :return: a dict of participant information based on the @ID lines.
        Key = participant code. Value = dict of info for the participant
        :rtype: dict
        """
        try:
            return self.metadata()['Participants']
        except KeyError:
            return dict()

    def participant_codes(self):
        """
        :return: a set of the speaker codes (e.g., `{'CHI', 'MOT', 'FAT'}`)
        :rtype: set
        """
        try:
            return set(self.metadata()['Participants'].keys())
        except KeyError:
            return set()

    def languages(self):
        """
        :return: a set of languages based on the @Languages metadata
        :rtype: set
        """
        try:
            languages_line = self.metadata()['Languages']
        except KeyError:
            return set()

        languages_set = set()
        for language in languages_line.split(','):
            language = language.strip()
            languages_set.add(language)
        return languages_set

    def date(self):
        """
        Returns the date of recording.

        :return: a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``. Returns ``None`` instead
        of any errors arise (e.g., there's no date).
        :rtype: tuple, or None
        """
        try:
            date_str = self.metadata()['Date']
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
        try:
            age_str = self.metadata()['Participants'][speaker]['age']

            year, _semicolon, month_day = age_str.partition(';')
            month, _period, day = month_day.partition('.')

            year = int(year) if year.isdigit() else 0
            month = int(month) if month.isdigit() else 0
            day = int(day) if day.isdigit() else 0
            return year, month, day
        except (KeyError, IndexError, ValueError):
            return None
