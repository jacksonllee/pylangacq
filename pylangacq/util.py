
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
