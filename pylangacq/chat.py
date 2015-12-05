
class Reader:

    def __init__(self, filename):
        self.filename = filename

    def cha_lines(self):
        """
        Reads the .cha file and cleans it up by undoing the line continuation
        with the tab character.

        :return: a list iterator of all cleaned-up lines in the .cha file
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
        speaekr codes (e.g., 'CHI', 'MOT') and the value is a list of
        information for the respective speaker code. The list of information is
        in this order:

        speaker label (from the '@Participants' field), language, corpus, code,
        age, sex, group, SES, role, education, custom
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
                    outdict['Participants'][code] = [speaker_label]

            elif head == 'ID':
                speaker_info = line.split('|')[: -1]  # final empty str removed

                # speaker_info contains these in order:
                #   language, corpus, code, age, sex, group, SES, role,
                #   education, custom

                code = speaker_info[2]
                outdict['Participants'][code].extend(speaker_info)

            else:
                outdict[head] = line

        return outdict

    def age(self, speaker='CHI'):
        """
        Returns the age of a particular speaker.

        :param speaker: an optional argument to specify which speaker,
        default = ``'CHI'``
        :return: a 3-tuple of (*year*, *month*, *day*),
        where *year*, *month*, *day* are all ``int``.
        """
        age_str = self.metadata()['Participants'][speaker][4]

        year, _semicolon, month_day = age_str.partition(';')
        month, _period, day = month_day.partition('.')

        year = int(year) if year.isdigit() else 0
        month = int(month) if month.isdigit() else 0
        day = int(day) if day.isdigit() else 0

        return year, month, day
