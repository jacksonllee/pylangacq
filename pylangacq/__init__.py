import os
from pylangacq.chat import Reader
from pylangacq.util import ENCODING

VERSION_ERROR = 'unknown version; VERSION file not found'
version_filename = os.path.join(os.path.dirname(__file__), 'VERSION')

try:
    with open(version_filename) as f:
        __version__ = f.read().strip()
except FileNotFoundError:
    __version__ = VERSION_ERROR


def read_chat(*filenames, encoding=ENCODING):
    """
    Create a ``Reader`` object based on *filenames*.

    :param filenames: one or multiple filenames (absolute-path or relative to
        the current directory; with or without glob matching patterns)

    :param encoding: file encoding; defaults to 'utf8'. (New in version 0.9)
    """
    return Reader(*filenames, encoding=encoding)
