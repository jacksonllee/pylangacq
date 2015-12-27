import re

# CLITIC is a str constant to represent what would be a clitic in tagged data.
CLITIC = 'CLITIC'


def startswithoneof(inputstr, seq):
    """
    Checks if inputstr starts with one of the items in seq. If it does, return
    the item that it starts with. If it doe not, return None.

    :param inputstr: input string
    :param seq: sequences of items to check
    :return: the item the the input string starts with (None if not found)
    :rtype: str or None
    """
    seq = set(seq)
    for item in seq:
        if inputstr.startswith(item):
            return item
    else:
        return None

def endswithoneof(inputstr, seq):
    """
    Checks if inputstr ends with one of the items in seq. If it does, return
    the item that it ends with. If it doe not, return None.

    :param inputstr: input string
    :param seq: sequences of items to check
    :return: the item the the input string ends with (None if not found)
    :rtype: str or None
    """
    seq = set(seq)
    for item in seq:
        if inputstr.endswith(item):
            return item
    else:
        return None

def find_indices(longstr, substring):
    """
    Finds all indices of non-overlapping occurrences of substring in longstr

    :param longstr: the long string
    :param substring: the substring to find
    :return: list of indices of the long string for where substring occurs
    :rtype: list
    """
    return [m.start() for m in re.finditer(substring, longstr)]

def replace_all(inputstr, replacee_replacer_pairs):
    """
    :param inputstr: input string
    :param replacee_replacer_pairs: pairs of (replacee, replacer)
    :return: string with all replacees replaced by their respective replacers
    """
    for replacee, replacer in replacee_replacer_pairs:
        inputstr = inputstr.replace(replacee, replacer)
    return inputstr

