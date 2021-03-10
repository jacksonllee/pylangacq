import dataclasses
from typing import Dict, List, Tuple, Union


@dataclasses.dataclass
class Gra:
    """Grammatical relation of a word in an utterance.

    Attributes
    ----------
    source : int
        The current word's position in the utterance; counting starts from 1.
    target : int
        The target word's position in the utterance; counting starts from 1.
    rel : str
        Grammatical relation
    """

    __slots__ = ("source", "target", "rel")

    source: int
    target: int
    rel: str


@dataclasses.dataclass
class Token:
    """Token with attributes as parsed from a CHAT utterance.

    Attributes
    ----------
    word : str
        Word form of the token
    pos : str
        Part-of-speech tag
    mor : str
        Morphological information
    gra : Gra
        Grammatical relation
    """

    __slots__ = ("word", "pos", "mor", "gra")

    word: str
    pos: Union[str, None]
    mor: Union[str, None]
    gra: Union[Gra, None]


@dataclasses.dataclass
class Utterance:
    """TODO"""

    __slots__ = ("participant", "tokens", "time_marks", "tiers")

    participant: str
    tokens: List[Token]
    time_marks: Union[Tuple[int, int], None]
    tiers: Dict[str, str]
