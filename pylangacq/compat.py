"""Compatibility between Python 2 and 3."""

import sys
import io


if sys.version_info[0] == 2:  # pragma: no coverage
    open = io.open
    unicode_ = unicode  # noqa F821 (undefined name 'unicode' in python >= 3)
    OPEN_MODE = 'rU'
else:  # pragma: no coverage
    open = open
    unicode_ = str
    # 'U' deprecated since python 3.4, to removed in python 4.0
    # https://docs.python.org/3/library/functions.html#open
    OPEN_MODE = 'r'


try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = IOError
