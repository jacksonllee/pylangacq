try:
    from importlib.metadata import version
except ModuleNotFoundError:
    # For Python 3.7
    from importlib_metadata import version

from .chat import read_chat, Reader


__version__ = version("pylangacq")

__all__ = ["__version__", "read_chat", "Reader"]
