import pkg_resources

from pylangacq.chat import read_chat, Reader


__version__ = pkg_resources.get_distribution("pylangacq").version

__all__ = ["__version__", "read_chat", "Reader"]
