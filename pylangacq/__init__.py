import os
from pylangacq.chat import Reader

VERSION_ERROR = 'unknown version; VERSION file not found'
version_filename = os.path.join(os.path.dirname(__file__), 'VERSION')

try:
    with open(version_filename) as f:
        __version__ = f.read().strip()
except FileNotFoundError:
    __version__ = VERSION_ERROR


def read_chat(*filenames):
    """
    Create a ``Reader`` object based on *filenames.

    :param filenames: one or multiple filenames (absolute-path or relative to
        the current directory; with or without glob matching patterns)
    """
    return Reader(*filenames)
