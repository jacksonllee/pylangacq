import os

version_filename = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(version_filename) as f:
    __version__ = f.read().strip()
