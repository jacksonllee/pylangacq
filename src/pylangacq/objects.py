import dataclasses
from typing import Dict, List, Tuple, Union

from tabulate import tabulate

from ._punctuation_marks import _PUNCTUATION_MARKS


_POSTCLITIC = "POSTCLITIC"
_PRECLITIC = "PRECLITIC"
_CLITICS = frozenset([_PRECLITIC, _POSTCLITIC])


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

    def to_mor_tier(self) -> str:
        """Return the %mor representation.

        Returns
        -------
        str
        """
        if self.word in _PUNCTUATION_MARKS:
            return self.word
        else:
            return f"{self.pos or ''}|{self.mor or ''}"

    def to_gra_tier(self) -> str:
        """Return the %gra representation.

        Returns
        -------
        str
        """
        return f"{self.gra.dep}|{self.gra.head}|{self.gra.rel}"


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

    def _to_str(self, tabular: bool = True) -> str:
        # `mor_gra_keys` needs to be a list for the ordering.
        mor_gra_keys = [key for key in ("%mor", "%gra") if key in self.tiers.keys()]
        if tabular and mor_gra_keys:
            tokens_in_table = []
            prev_token = None
            for token in self.tokens:
                token_in_table = []
                # TODO: Write a test for the clitic case.
                if token.word == _POSTCLITIC and prev_token is not None:
                    tokens_in_table.pop()
                    token_in_table.append(prev_token.word)
                    if "%mor" in mor_gra_keys:
                        token_in_table.append(
                            f"{prev_token.to_mor_tier()}~{token.to_mor_tier()}"
                        )
                    if "%gra" in mor_gra_keys:
                        token_in_table.append(
                            f"{prev_token.to_gra_tier()} {token.to_gra_tier()}"
                        )
                else:
                    token_in_table.append(token.word)
                    if "%mor" in mor_gra_keys:
                        token_in_table.append(token.to_mor_tier())
                    if "%gra" in mor_gra_keys:
                        token_in_table.append(token.to_gra_tier())
                prev_token = token
                tokens_in_table.append(token_in_table)
            tokens_in_table_with_keys = [
                [f"*{self.participant}:"] + [f"{key}:" for key in mor_gra_keys],
                *tokens_in_table,
            ]
            # Transpose (see https://stackoverflow.com/a/6473724)
            tiers_in_table = list(map(list, zip(*tokens_in_table_with_keys)))
            str_for_u = f"{tabulate(tiers_in_table, tablefmt='plain')}\n"
        else:
            str_for_u = f"*{self.participant}:\t{self.tiers[self.participant]}\n"
            for key in mor_gra_keys:
                str_for_u += f"{key}:\t{self.tiers[key]}\n"

        keys = _sort_keys(self.tiers.keys(), drop={self.participant, "%mor", "%gra"})
        for key in keys:
            str_for_u += f"{key}:\t{self.tiers[key]}\n"

        return str_for_u

    def _repr_html_(self):
        html = ""

        # Row from words
        cells = [
            f'    <td style="text-align: left">{t.word}</td>\n' for t in self.tokens
        ]
        html += (
            "  <tr>\n"
            f"    <td>*{self.participant}:</td>\n"
            f"{''.join(cells)}"
            "  </tr>\n"
        )

        # Row from %mor
        if "%mor" in self.tiers:
            cells = [
                f'    <td style="text-align: left">{t.to_mor_tier()}</td>\n'
                for t in self.tokens
            ]
            html += "  <tr>\n" "    <td>%mor:</td>\n" f"{''.join(cells)}" "  </tr>\n"

        # Row from %gra
        if "%gra" in self.tiers:
            cells = [
                f'    <td style="text-align: left">{t.to_gra_tier()}</td>\n'
                for t in self.tokens
            ]
            html += "  <tr>\n" "    <td>%gra:</td>\n" f"{''.join(cells)}" "  </tr>\n"

        keys = _sort_keys(self.tiers.keys(), drop={self.participant, "%mor", "%gra"})
        for key in keys:
            html += (
                f"  <tr>\n"
                f"    <td>{key}:</td>\n"
                f'    <td colspan="{len(self.tokens)}" style="text-align: left">'
                f"{self.tiers[key]}</td>\n"
                f"  </tr>\n"
            )

        return f"<table>{html}</table>"


def _sort_keys(keys, *, first=None, drop=None) -> List[str]:
    sorted_keys = []
    first = first or []
    drop = set(drop or [])  # ordering doesn't matter
    for key in first:
        if key in keys:
            sorted_keys.append(key)
    for key in keys:
        if not (key in sorted_keys or key in drop):
            sorted_keys.append(key)
    return sorted_keys
