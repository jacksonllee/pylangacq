# -*- coding: utf-8 -*-

import re

# CLITIC is a str constant to represent what would be a clitic in tagged data.
CLITIC = 'CLITIC'
ALL_PARTICIPANTS = '**ALL**'
ENCODING = 'utf8'


def startswithoneof(inputstr, seq):
    """
    Check if *inputstr* starts with one of the items in seq. If it does, return
        the item that it starts with. If it doe not, return ``None``.

    :param inputstr: input string

    :param seq: sequences of items to check

    :return: the item the the input string starts with (``None`` if not found)

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
    Check if *inputstr* ends with one of the items in seq. If it does, return
        the item that it ends with. If it doe not, return ``None``.

    :param inputstr: input string

    :param seq: sequences of items to check

    :return: the item the the input string ends with (``None`` if not found)

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
    Find all indices of non-overlapping occurrences of substring in *longstr*

    :param longstr: the long string

    :param substring: the substring to find

    :return: list of indices of the long string for where substring occurs

    :rtype: list
    """
    return [m.start() for m in re.finditer(substring, longstr)]


def replace_all(inputstr, replacee_replacer_pairs):
    """
    Replace in *inputstr* all replacers by the corresponding replacees in
        *replacee_replacer_pairs*.

    :param inputstr: input string

    :param replacee_replacer_pairs: pairs of (replacee, replacer)

    :return: string with all replacees replaced by their respective replacers
    """
    for replacee, replacer in replacee_replacer_pairs:
        inputstr = inputstr.replace(replacee, replacer)
    return inputstr


def remove_extra_spaces(inputstr):
    """
    Remove extra spaces in *inputstr* so that there are only single
        (but not double, triple etc) spaces.

    :param inputstr: input string

    :return: string with replacers replaced by corresponding replacees
    """
    while '  ' in inputstr:
        inputstr = inputstr.replace('  ', ' ')
    return inputstr.strip()


class ListFromIterables(list):
    """
    A class like ``list`` that can be initialized with iterables.
    """
    def __init__(self, *iterables):
        super(ListFromIterables, self).__init__()
        self.input_iterables = iterables
        self.from_iterables()

    def from_iterables(self):
        for it in self.input_iterables:
            for element in it:
                self.append(element)
