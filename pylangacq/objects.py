import dataclasses
from typing import Dict, List, Tuple, Union


@dataclasses.dataclass
class Gra:
    """Grammatical relation of a word in an utterance.

    Attributes
    ----------
    dep : int
        The position of the dependent (i.e., the word itself) in the utterance
    head : int
        The position of the head in the utterance
    rel : str
        Grammatical relation
    """

    __slots__ = ("dep", "head", "rel")

    dep: int
    head: int
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
    """Utterance in a CHAT transcript data.

    Attributes
    ----------
    participant : str
        Participant of the utterance, e.g., ``"CHI"``, ``"MOT"``
    tokens : List[Token]
        List of tokens of the utterance
    time_marks : Tuple[int, int]
        If available from the CHAT data, these are the start and end times
        (in milliseconds) for a segment in a digitized video or audio file,
        e.g., ``(0, 1073)``, extracted from ``"·0_1073·"`` in the CHAT data.
        ``"·"`` is ASCII code 21 (0x15), for NAK (Negative Acknowledgment).
    tiers : Dict[str, str]
        This dictionary contains all the original, unparsed data from the utterance,
        including the transcribed utterance (signaled by ``*CHI:``, ``*MOT:`` etc
        in CHAT), common tiers such as %mor and %gra, as well as all other tiers
        associated with the utterance. This dictionary is useful to retrieve
        whatever information not readily handled by this package.
    """

    __slots__ = ("participant", "tokens", "time_marks", "tiers")

    participant: str
    tokens: List[Token]
    time_marks: Union[Tuple[int, int], None]
    tiers: Dict[str, str]
