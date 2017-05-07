# -*- coding: utf-8 -*-

import os
from pylangacq.chat import ENCODING, Reader


with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
    __version__ = f.read().strip()


def read_chat(*filenames, encoding=ENCODING):
    """
    Create a ``Reader`` object based on *filenames*.

    :param filenames: one or multiple filenames (absolute-path or relative to
        the current directory; with or without glob matching patterns)

    :param encoding: file encoding; defaults to 'utf8'. (New in version 0.9)
    """
    return Reader(*filenames, encoding=encoding)
