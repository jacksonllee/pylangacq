# -*- coding: utf-8 -*-

import os

from pylangacq.chat import read_chat


with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
    __version__ = f.read().strip()


__all__ = ['read_chat']
