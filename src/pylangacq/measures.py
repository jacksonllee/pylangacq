from typing import List

from .dependency import _DependencyGraph
from .objects import _POSTCLITIC


_WORDS_IGNORE_WHOLE_UTTERANCE = frozenset({"xxx", "yyy", "www"})
_POS_TO_IGNORE = frozenset({"", "!", "+...", "0", "?", "BEG"})
_WORDS_TO_IGNORE = frozenset(
    {
        "",
        "!",
        "+...",
        ".",
        ",",
        "?",
        "‡",
        "„",
        "0",
        _POSTCLITIC,
    }
)


def _get_lemma_from_mor(mor):
    """Extract lemma from ``mor``.

    Parameters
    ----------
    mor : tuple(str, str, str)

    Returns
    -------
    str
    """
    lemma, _, _ = mor.partition("-")
    lemma, _, _ = lemma.partition("&")
    return lemma


def _get_mlum(tagged_sents, exclude_switch) -> List[float]:
    result = []

    if not tagged_sents:
        return result

    for tagged_sents_for_file in tagged_sents:
        if not tagged_sents_for_file:
            result.append(0.0)
            continue

        morpheme_counts_for_file = []
        for tokens in tagged_sents_for_file:
            morpheme_count = 0
            exclude_utterance = False
            for token in tokens:
                if token.word in _WORDS_IGNORE_WHOLE_UTTERANCE:
                    exclude_utterance = True
                    break
                if exclude_switch and token.word.endswith("@s"):
                    continue
                if token.pos in _POS_TO_IGNORE:
                    continue
                morpheme_count += 1
                if type(token.mor) is str:
                    morpheme_count += token.mor.count("-")
                    morpheme_count += token.mor.count("~")
                    morpheme_count += token.mor.count("$")
            if exclude_utterance or not morpheme_count:
                continue
            morpheme_counts_for_file.append(morpheme_count)

        if morpheme_counts_for_file:
            result.append(sum(morpheme_counts_for_file) / len(morpheme_counts_for_file))
        else:
            result.append(0.0)

    return result


def _get_mluw(sents, exclude_switch) -> List[float]:
    result = []

    if not sents:
        return result

    for sents_for_file in sents:
        if not sents_for_file:
            result.append(0.0)
            continue

        word_counts_for_file = []
        for sent in sents_for_file:
            exclude_utterance = False
            for word in sent:
                if word in _WORDS_IGNORE_WHOLE_UTTERANCE:
                    exclude_utterance = True
                    break
            if exclude_utterance:
                continue
            word_count = sum(
                1
                for word in sent
                if word not in _WORDS_TO_IGNORE
                and (not exclude_switch or not word.endswith("@s"))
            )
            if not word_count:
                continue
            word_counts_for_file.append(word_count)

        if word_counts_for_file:
            result.append(sum(word_counts_for_file) / len(word_counts_for_file))
        else:
            result.append(0.0)

    return result


def _get_ttr(word_freq_dicts) -> List[float]:
    result_by_files = []
    for word_freq in word_freq_dicts:
        filtered = {w: f for w, f in word_freq.items() if w not in _WORDS_TO_IGNORE}
        try:
            result_by_files.append(len(filtered) / sum(filtered.values()))
        except ZeroDivisionError:
            result_by_files.append(0.0)
    return result_by_files


def _get_ipsyn(tagged_sents) -> List[int]:
    result_by_files = []
    for tagged_sents_for_file in tagged_sents:
        result_by_files.append(_get_ipsyn_for_file(tagged_sents_for_file))
    return result_by_files


def _get_ipsyn_for_file(tagged_sents) -> int:
    """Index of Productive Syntax (IPSyn)"""
    if len(tagged_sents) > 100:
        tagged_sents = tagged_sents[:100]

    scoring_board = {
        "N1": 0,
        "N2": 0,
        "N3": 0,
        "N4": 0,
        "N5": 0,
        "N6": 0,
        "N7": 0,
        "N8": 0,
        "N9": 0,
        "N10": 0,
        "N11": 0,
        "V1": 0,
        "V2": 0,
        "V3": 0,
        "V4": 0,
        "V5": 0,
        "V6": 0,
        "V7": 0,
        "V8": 0,
        "V9": 0,
        "V10": 0,
        "V11": 0,
        "V12": 0,
        "V13": 0,
        "V14": 0,
        "V15": 0,
        "V16": 0,
        "Q1": 0,
        "Q2": 0,
        "Q3": 0,
        "Q4": 0,
        "Q5": 0,
        "Q6": 0,
        "Q7": 0,
        "Q8": 0,
        "Q9": 0,
        "Q10": 0,
        "S1": 0,
        "S2": 0,
        "S3": 0,
        "S4": 0,
        "S5": 0,
        "S6": 0,
        "S7": 0,
        "S8": 0,
        "S9": 0,
        "S10": 0,
        "S11": 0,
        "S12": 0,
        "S13": 0,
        "S14": 0,
        "S15": 0,
        "S16": 0,
        "S17": 0,
        "S18": 0,
        "S19": 0,
    }

    scoring_board_stop = {
        "N1": False,
        "N2": False,
        "N3": False,
        "N4": False,
        "N5": False,
        "N6": False,
        "N7": False,
        "N8": False,
        "N9": False,
        "N10": False,
        "N11": False,
        "V1": False,
        "V2": False,
        "V3": False,
        "V4": False,
        "V5": False,
        "V6": False,
        "V7": False,
        "V8": False,
        "V9": False,
        "V10": False,
        "V11": False,
        "V12": False,
        "V13": False,
        "V14": False,
        "V15": False,
        "V16": False,
        "Q1": False,
        "Q2": False,
        "Q3": False,
        "Q4": False,
        "Q5": False,
        "Q6": False,
        "Q7": False,
        "Q8": False,
        "Q9": False,
        "Q10": False,
        "S1": False,
        "S2": False,
        "S3": False,
        "S4": False,
        "S5": False,
        "S6": False,
        "S7": False,
        "S8": False,
        "S9": False,
        "S10": False,
        "S11": False,
        "S12": False,
        "S13": False,
        "S14": False,
        "S15": False,
        "S16": False,
        "S17": False,
        "S18": False,
        "S19": False,
    }

    def add_one_point_if_needed(item):
        """
        Add one point to *item* if necessary. If *item* has scored 2 points,
        avoid further scoring by setting scoring_board_stop[*item*] to True.

        :param item: check item like 'N1', 'Q3' etc
        """
        if not scoring_board_stop[item]:
            scoring_board[item] += 1
        else:
            return

        if scoring_board[item] >= 2:
            scoring_board_stop[item] = True

    def turn_off_scoring_board(item):
        """
        Check if scoring_board[*item*] is already 2 and, if so: (i) set
        scoring_board_stop[*item*] to True, and (ii) return True.
        Return False otherwise.

        :param item: check item like 'N1', 'Q3' etc
        """
        if scoring_board[item] >= 2:
            scoring_board_stop[item] = True
            return True
        else:
            return False

    def test_item(item_function):
        item = item_function.__name__

        for tagged_sent in tagged_sents:
            if scoring_board_stop[item]:
                break

            sent_graph = _DependencyGraph(tagged_sent)
            if sent_graph.faulty:
                continue

            item_function(sent_graph)

            if turn_off_scoring_board(item):
                break

    @test_item
    def N1(graph):
        """
        N1: Proper, mass, or count noun
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos.startswith("n:") or pos == "n":
                scoring_board["N1"] += 1

            if turn_off_scoring_board("N1"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N2(graph):
        """
        N2: Pronoun or prolocative, excluding modifiers
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos.startswith("pro") and pos != "pro:poss:det":
                scoring_board["N2"] += 1

            if turn_off_scoring_board("N2"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N3(graph):
        """
        N3: Modifier, including adjectives, possessives, and quantifiers
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos in {"pro:poss:det", "adj", "qn"}:
                scoring_board["N3"] += 1

            if turn_off_scoring_board("N3"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N4(graph):
        """
        N4: Two-word NP: nominal preceded by article or modifier
        """
        if not graph.n_nodes() > 2:
            return

        for i in range(1, graph.n_nodes() - 1):
            pos1 = graph.node[i]["pos"]
            pos2 = graph.node[i + 1]["pos"]

            if pos1 in {"pro:poss:det", "adj", "qn"} and (
                pos2.startswith("n:") or pos2 == "n"
            ):
                scoring_board["N4"] += 1

            if turn_off_scoring_board("N4"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N5(graph):
        """
        N5: Article, used before a noun (Also credit: N4)
        """
        if not graph.n_nodes() > 2:
            return

        for i in range(1, graph.n_nodes() - 1):
            pos1 = graph.node[i]["pos"]
            pos2 = graph.node[i + 1]["pos"]

            if pos1 == "det" and (pos2.startswith("n:") or pos2 == "n"):
                scoring_board["N5"] += 1
                add_one_point_if_needed("N4")

            if turn_off_scoring_board("N5"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N6(graph):
        """
        N6: Two-word NP (as in N4) after verb or preposition (Also credit: N4)
        """
        if not graph.n_nodes() > 3:
            return

        for i in range(1, graph.n_nodes() - 2):
            pos1 = graph.node[i]["pos"]
            pos2 = graph.node[i + 1]["pos"]
            pos3 = graph.node[i + 2]["pos"]

            if (
                pos2 in {"pro:poss:det", "adj", "qn"}
                and (pos3.startswith("n:") or pos3 == "n")
                and (pos1 in {"v", "prep"})
            ):
                scoring_board["N6"] += 1
                add_one_point_if_needed("N4")

            if turn_off_scoring_board("N6"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N7(graph):
        """
        N7: Plural suffix
        """
        for i in range(1, graph.n_nodes()):
            mor = graph.node[i]["mor"]

            if "-PL" in mor:
                scoring_board["N7"] += 1

            if turn_off_scoring_board("N7"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N8(graph):
        """
        N8: Two-word NP (as in N4) before verb (Also credit: N4)
        """
        if not graph.n_nodes() > 3:
            return

        for i in range(1, graph.n_nodes() - 2):
            pos1 = graph.node[i]["pos"]
            pos2 = graph.node[i + 1]["pos"]
            pos3 = graph.node[i + 2]["pos"]

            if (
                pos1 in {"pro:poss:det", "adj", "qn"}
                and (pos2.startswith("n:") or pos2 == "n")
                and (pos3 == "v")
            ):
                scoring_board["N8"] += 1
                add_one_point_if_needed("N4")

            if turn_off_scoring_board("N8"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N9(graph):
        """
        N9: Three-word NP (Det/Mod+Mod+N) (Also credit: N4)
        """
        if not graph.n_nodes() > 3:
            return

        for i in range(1, graph.n_nodes() - 2):
            pos1 = graph.node[i]["pos"]
            pos2 = graph.node[i + 1]["pos"]
            pos3 = graph.node[i + 2]["pos"]

            if (
                (pos1 in {"pro:poss:det", "adj", "qn"})
                and (pos2 in {"adj", "qn"})
                and (pos3.startswith("n:") or pos3 == "n")
            ):
                scoring_board["N9"] += 1
                add_one_point_if_needed("N4")

            if turn_off_scoring_board("N9"):
                break

    # noinspection PyPep8Naming
    @test_item
    def N10(graph):
        """
        N10: Adverb modifying adjective or nominal (Also credit: V8)
        """
        if not graph.n_nodes() > 2:
            return

        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos == "adv":
                for j in graph.edge[i].keys():
                    pos_of_head = graph.node[j]["pos"]

                    if pos_of_head in {"adj", "n"}:
                        scoring_board["N10"] += 1
                        add_one_point_if_needed("V8")
                        break

                if turn_off_scoring_board("N10"):
                    break

    # noinspection PyPep8Naming
    @test_item
    def N11(graph):
        """
        N11: Any other bound morpheme on N or adjective
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos in {"n", "adj"} or pos.startswith("n:"):
                mor = graph.node[i]["mor"]
                mor = mor.replace("-PL", "")

                if "-" in mor:
                    scoring_board["N11"] += 1

                if turn_off_scoring_board("N11"):
                    break

    # noinspection PyPep8Naming
    @test_item
    def V1(graph):
        """
        V1: Verb
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos == "v":
                scoring_board["V1"] += 1

            if turn_off_scoring_board("V1"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V2(graph):
        """
        V2: Particle or Preposition
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos == "prep":
                scoring_board["V2"] += 1

            if turn_off_scoring_board("V2"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V3(graph):
        """
        V3: Prepositional phrase (Prep + NP) (Also credit: V2)
        """
        for i in range(1, graph.n_nodes()):
            for j in graph.edge[i].keys():
                if graph.edge[i][j]["rel"] == "POBJ":
                    scoring_board["V3"] += 1
                    add_one_point_if_needed("V2")

                if turn_off_scoring_board("V3"):
                    break

    # noinspection PyPep8Naming
    @test_item
    def V4(graph):
        """
        V4: Copula linking two nominals (Also credit: V1)
        """
        if not graph.n_nodes() > 3:
            return

        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]
            if pos != "cop":
                continue

            subject = False
            predicate = False

            for dep, head in graph.edges().items():
                if head != i:
                    continue

                if graph.edge[dep][head]["rel"] == "SUBJ" and not graph.node[dep][
                    "pos"
                ].endswith("wh"):
                    subject = True
                elif graph.edge[dep][head]["rel"] == "PRED":
                    predicate = True

            if subject and predicate:
                scoring_board["V4"] += 1
                add_one_point_if_needed("V1")

            if turn_off_scoring_board("V4"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V5(graph):
        """
        V5: Catenative (pseudo-auxiliary) preceding a verb
        """
        if not graph.n_nodes() > 2:
            return

        pseudo_aux = {
            "hafta",
            "haf(ta)",
            "s'pose(da)",
            "s'poseda",
            "gonna",
            "gon(na)",
            "wanna",
            "wanta",
            "wan(t)(a)",
            "want(a)",
            "wan(na)",
            "gotta",
            "got(ta)",
            "better",
        }

        for i in range(1, graph.n_nodes() - 1):
            pos2 = graph.node[i + 1]["pos"]
            if pos2 != "v":
                continue

            word1 = graph.node[i]["word"]

            if word1 in pseudo_aux:
                scoring_board["V5"] += 1

            if turn_off_scoring_board("V5"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V6(graph):
        """
        V6: Auxiliary be, do, have in VP (Also credit: V5)
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]
            mor = graph.node[i]["mor"]
            lemma = _get_lemma_from_mor(mor)

            if (pos == "aux" and not mor.startswith("wi")) or (
                lemma == "do" and pos == "mod"
            ):
                scoring_board["V6"] += 1
                add_one_point_if_needed("V5")

            if turn_off_scoring_board("V6"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V7(graph):
        """
        V7: Progressive suffix
        """
        for i in range(1, graph.n_nodes()):
            mor = graph.node[i]["mor"]

            if mor.endswith("PRESP"):
                scoring_board["V7"] += 1

            if turn_off_scoring_board("V7"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V8(graph):
        """
        V8: Adverbs
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos == "adv":
                scoring_board["V8"] += 1

            if turn_off_scoring_board("V8"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V9(graph):
        """
        V9: Modal preceding verb (Also credit: V5)
        """
        if not graph.n_nodes() > 2:
            return

        for i in range(1, graph.n_nodes() - 1):
            pos = graph.node[i]["pos"]
            word = graph.node[i]["word"]
            pos2 = graph.node[i + 1]["pos"]

            if pos.startswith("mod") and pos2 == "v" and word != _POSTCLITIC:
                scoring_board["V9"] += 1
                add_one_point_if_needed("V5")

            if turn_off_scoring_board("V9"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V10(graph):
        """
        V10: Third person singular present tense suffix
        """
        for i in range(1, graph.n_nodes()):
            mor = graph.node[i]["mor"]

            if "-3S" in mor:
                scoring_board["V10"] += 1

            if turn_off_scoring_board("V10"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V11(graph):
        """
        V11: Past tense modal (Also credit V9)
        """
        past_tense_modals = {"could", "did", "might", "would", "woudn't"}

        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos != "mod":
                continue

            if graph.node[i]["word"] in past_tense_modals:
                scoring_board["V11"] += 1
                add_one_point_if_needed("V9")

            if turn_off_scoring_board("V11"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V12(graph):
        """
        V12: Regular past tense suffix
        """
        for i in range(1, graph.n_nodes()):
            mor = graph.node[i]["mor"]

            if "-PAST" in mor and "-PASTP" not in mor:
                scoring_board["V12"] += 1

            if turn_off_scoring_board("V12"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V13(graph):
        """
        V13: Past tense auxiliary (Also credit V6)
        """
        aux_pos = {"aux", "mod"}

        for i in range(1, graph.n_nodes()):
            mor = graph.node[i]["mor"]
            pos = graph.node[i]["pos"]

            if "&PAST" in mor and pos in aux_pos:
                scoring_board["V13"] += 1
                add_one_point_if_needed("V6")

            if turn_off_scoring_board("V13"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V14(graph):
        """
        V14: Medial adverb (Also credit V8)
        """
        for i in range(2, graph.n_nodes() - 1):
            # note the possible values of i for "medial" (not 1st or last word)

            pos = graph.node[i]["pos"]
            if pos == "adv":
                scoring_board["V14"] += 1
                add_one_point_if_needed("V8")

            if turn_off_scoring_board("V14"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V15(graph):
        """
        V15: Copula, modal, or auxiliary for emphasis or ellipsis
        (uncontractible context) (Also credit V4, V6, V9, V11, V13, V16)
        """
        if not graph.n_nodes() > 2:
            return

        for i in range(1, graph.n_nodes() - 1):
            pos1 = graph.node[i]["pos"]

            if pos1 not in {"cop", "aux", "mod"}:
                continue

            mor2 = graph.node[i + 1]["mor"]

            if mor2 in {"", "beg", "end"}:  # if mor2 is a punctuation
                scoring_board["V15"] += 1
                add_one_point_if_needed("V4")
                add_one_point_if_needed("V6")
                add_one_point_if_needed("V9")
                add_one_point_if_needed("V11")
                add_one_point_if_needed("V13")
                add_one_point_if_needed("V16")

            if turn_off_scoring_board("V15"):
                break

    # noinspection PyPep8Naming
    @test_item
    def V16(graph):
        """
        V16: Past tense copula (Also credit V4)
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]
            mor = graph.node[i]["mor"]

            if pos.startswith("cop") and "PAST" in mor:
                scoring_board["V16"] += 1
                add_one_point_if_needed("V4")

            if turn_off_scoring_board("V16"):
                break

    # noinspection PyPep8Naming
    @test_item
    def Q1(graph):
        """
        Q1: Intonationally marked question
        Automatically score 2 points if child earns 2 points on Q4 and/or Q8
        """
        final_word = graph.node[graph.n_nodes() - 1]["word"]
        if final_word != "?":
            return

        first_word = graph.node[1]["word"]
        if first_word in {"what", "why", "how", "which", "where", "when"}:
            return

        scoring_board["Q1"] += 1

        if turn_off_scoring_board("Q1"):
            pass

    # noinspection PyPep8Naming
    @test_item
    def Q2(graph):
        """
        Q2: Routine do/go or existence/name question or wh-pronoun alone
        Automatically score 2 points if child earns 2 points on Q4 and/or Q8
        """
        # needs work here
        # currently only testing for wh-pronoun alone
        final_word = graph.node[graph.n_nodes() - 1]["word"]
        if final_word != "?":
            return

        first_word = graph.node[1]["word"]
        if first_word not in {"what", "why", "how", "which", "where", "when"}:
            return

        if graph.n_nodes() > 2:
            scoring_board["Q2"] += 1

        if turn_off_scoring_board("Q2"):
            pass

    # noinspection PyPep8Naming
    @test_item
    def Q3(graph):
        """
        Q3: Simple negation (neg + X):
        neg = no(t), can't, don't
        X = NP, VP, PP, Adj, Adv, etc.
        """
        if not graph.n_nodes() > 2:
            return

        for i in range(1, graph.n_nodes() - 1):
            word1 = graph.node[i]["word"]
            mor2 = graph.node[i + 1]["mor"]

            if word1 in {"no", "not", "can't", "don't"} and mor2 not in {
                "",
                "beg",
                "end",
            }:
                scoring_board["Q3"] += 1

            if turn_off_scoring_board("Q3"):
                break

    # noinspection PyPep8Naming
    @test_item
    def Q4(graph):
        """
        Q4: Initial wh-pronoun followed by verb
        (if child earns 2 points for Q8, score 2 points to *both* Q1 and Q2)
        """
        if not graph.n_nodes() > 2:
            return
        final_word = graph.node[graph.n_nodes() - 1]["word"]
        if final_word != "?":
            return

        first_word = graph.node[1]["word"]
        if first_word not in {"what", "why", "how", "which", "where", "when"}:
            return

        root = graph.edges()[1]

        if graph.node[root]["pos"] == "v":
            scoring_board["Q4"] += 1

        if turn_off_scoring_board("Q4"):
            scoring_board["Q1"] = 2
            scoring_board["Q2"] = 2
            scoring_board_stop["Q1"] = True
            scoring_board_stop["Q2"] = True

    # noinspection PyPep8Naming
    @test_item
    def Q5(graph):
        """
        Q5: Negative morpheme between subject and verb (Also credit: Q3)
        """
        if not graph.n_nodes() > 3:
            return

        for dep, head in graph.edges().items():
            if dep > head:
                continue

            rel = graph.edge[dep][head]["rel"]

            if rel != "SUBJ":
                continue

            head_pos = graph.node[head]["pos"]

            if head_pos != "V":
                continue

            for i in range(dep + 1, head):  # head > dep
                if graph.node[i]["pos"] == "neg":
                    scoring_board["Q5"] += 1
                    add_one_point_if_needed("Q3")
                    break

            if turn_off_scoring_board("Q5"):
                break

    # noinspection PyPep8Naming
    @test_item
    def Q6(graph):
        """
        Q6: Wh-question with inverted modal, copula, or auxiliary
        """
        if not graph.n_nodes() > 2:
            return

        for i in range(1, graph.n_nodes()):
            if scoring_board_stop["Q6"]:
                break

            pos = graph.node[i]["pos"]

            if pos not in {"cop", "mod", "aux"}:
                continue

            for dep, head in graph.edges().items():
                if head != i:
                    continue

                if dep > head:
                    continue
                    # we want "inversion" (= dep-wh comes before head-V)

                pos_of_dep = graph.node[dep]["pos"]

                if pos_of_dep == "adv:wh":
                    scoring_board["Q6"] += 1

                if turn_off_scoring_board("Q6"):
                    break

    # noinspection PyPep8Naming
    @test_item
    def Q7(graph):
        """
        Q7: Negation of copula, modal, or auxiliary (Also credit Q5)
        """
        if not graph.n_nodes() > 2:
            return

        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos not in {"mod", "cop", "aux"}:
                continue

            for dep, head in graph.edges().items():
                if head != i:
                    continue

                pos_of_dep = graph.node[dep]["pos"]

                if pos_of_dep == "neg":
                    scoring_board["Q7"] += 1
                    add_one_point_if_needed("Q5")

                if turn_off_scoring_board("Q7"):
                    break

    # noinspection PyPep8Naming
    @test_item
    def Q8(graph):
        """
        Q8: Yes/no question with inverted modal, copula, or auxiliary
        (if child earns 2 points for Q8, score 2 points to *both* Q1 and Q2)
        """
        # test may need to be checked/improved
        if not graph.n_nodes() > 2:
            return

        final_word = graph.node[graph.n_nodes() - 1]["word"]
        if final_word != "?":
            return

        for i in range(1, graph.n_nodes() - 1):
            if scoring_board_stop["Q8"]:
                break

            pos1 = graph.node[i]["pos"]

            if i != 1:
                wh_test = graph.node[i - 1]["pos"]
            else:
                wh_test = "dummy"

            if pos1 in {"cop", "mod", "aux"} and not wh_test.endswith("wh"):
                for j in graph.edge[i + 1].keys():
                    rel2 = graph.edge[i + 1][j]["rel"]

                    if rel2 == "SUBJ":
                        scoring_board["Q8"] += 1

                    if turn_off_scoring_board("Q8"):
                        scoring_board["Q1"] = 2
                        scoring_board["Q2"] = 2
                        scoring_board_stop["Q1"] = True
                        scoring_board_stop["Q2"] = True
                        break

    # noinspection PyPep8Naming
    @test_item
    def Q9(graph):
        """
        Q9: Why, when, which, whose
        """
        wh = {"why", "when", "which", "whose"}
        for i in range(1, graph.n_nodes()):
            word = graph.node[i]["word"]
            if word in wh:
                scoring_board["Q9"] += 1

            if turn_off_scoring_board("Q9"):
                break

    # noinspection PyPep8Naming
    @test_item
    def Q10(graph):
        """
        Q10: Tag question
        """
        if not graph.n_nodes() > 2:
            return

        # Part 1: test for ending "okay ?", "ok ?", "right ?"
        final_word = graph.node[graph.n_nodes() - 1]["word"]
        if final_word != "?":
            return

        second_final_word = graph.node[graph.n_nodes() - 2]["word"]
        if second_final_word in {"okay", "ok", "right"}:
            scoring_board["Q10"] += 1

        if turn_off_scoring_board("Q10"):
            return

        # Part 2: test for "normal" tag questions
        good_pos = {"cop neg pro ?", "cop pro ?"}
        collate = []

        for i in range(1, graph.n_nodes()):
            collate.append(graph.node[i]["pos"])

        test = " ".join(collate)

        for tag in good_pos:
            if tag in test:
                scoring_board["Q10"] += 1

            if turn_off_scoring_board("Q10"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S1(graph):
        """
        S1: Two-word combination
        """
        if not graph.n_nodes() > 2:
            return

        scoring_board["S1"] += 1

        if turn_off_scoring_board("S1"):
            pass

    # noinspection PyPep8Naming
    @test_item
    def S2(graph):
        """
        S2: Subject-verb sequence (Also credit: S1)
        """
        if not graph.n_nodes() > 2:
            return

        for dep, head in graph.edges().items():
            if dep > head:
                continue

            rel = graph.edge[dep][head]["rel"]

            if rel != "SUBJ":
                continue

            head_pos = graph.node[head]["pos"]

            if head_pos == "v":
                scoring_board["S2"] += 1
                add_one_point_if_needed("S1")

            if turn_off_scoring_board("S2"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S3(graph):
        """
        S3: Verb-object sequence (Also credit: S1)
        """
        if not graph.n_nodes() > 2:
            return

        for dep, head in graph.edges().items():
            if dep < head:
                continue

            rel = graph.edge[dep][head]["rel"]

            if rel != "OBJ":
                continue

            head_pos = graph.node[head]["pos"]

            if head_pos == "v":
                scoring_board["S3"] += 1
                add_one_point_if_needed("S1")

            if turn_off_scoring_board("S3"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S4(graph):
        """
        S4: Subject-verb-object sequence (Also credit: S2 & S3)
        """
        if not graph.n_nodes() > 3:
            return

        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos != "v":
                continue

            has_subject = False
            has_object = False

            for dep, test_verb in graph.edges().items():
                if i != test_verb:
                    continue

                if dep < test_verb and graph.edge[dep][test_verb]["rel"] == "SUBJ":
                    has_subject = True

                if dep > test_verb and graph.edge[dep][test_verb]["rel"] == "OBJ":
                    has_object = True

            if has_subject and has_object:
                scoring_board["S4"] += 1
                add_one_point_if_needed("S2")
                add_one_point_if_needed("S3")

            if turn_off_scoring_board("S4"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S5(graph):
        """
        S5: Conjunction (any)
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos == "conj":
                scoring_board["S5"] += 1

            if turn_off_scoring_board("S5"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S6(graph):
        """
        S6: Sentence with two VPs
        """
        if not graph.n_nodes() > 4:
            return

        all_edges = graph.edges()
        verbs = []
        deps_of_verbs = []

        for dep, head in all_edges.items():
            head_pos = graph.node[head]["pos"]

            if head_pos != "v":
                continue

            verbs.append(head)
            deps_of_verbs.append(dep)

        if len(verbs) == 2 and tuple(verbs) not in list(all_edges.items()):
            scoring_board["S6"] += 1

        if turn_off_scoring_board("S6"):
            pass

    # noinspection PyPep8Naming
    @test_item
    def S7(graph):
        """
        S7: Conjoined phrases (Also credit: S5)
        """
        if not graph.n_nodes() > 3:
            return

        # for all trios, we want the middle word to be CONJ (for pos)
        # and the first+final words are *not* punctuation (for mor)
        for i in range(1, graph.n_nodes() - 2):
            mor1 = graph.node[i]["mor"]
            pos2 = graph.node[i + 1]["pos"]
            mor3 = graph.node[i + 2]["mor"]

            punctuations = {"", "beg", "end"}
            if pos2 == "conj" and mor1 not in punctuations and mor3 not in punctuations:
                scoring_board["S7"] += 1
                add_one_point_if_needed("S5")

            if turn_off_scoring_board("S7"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S8(graph):
        """
        S8: Infinitive without catenative, marked with "to"
        (Also credit: S6 & V5)
        """
        if not graph.n_nodes() > 3:
            return

        # we want:
        # -- main verb (ROOT for rel)
        # -- infinitive "to" with a head *not* being the main verb

        for dep, head in graph.edges().items():
            pos = graph.node[dep]["pos"]

            if pos != "inf":
                continue

            inf_verb = head

            for test_verb, new_head in graph.edges().items():
                if inf_verb != test_verb:
                    continue

                if not graph.edge[inf_verb][new_head]["rel"].endswith("ROOT"):
                    scoring_board["S8"] += 1
                    add_one_point_if_needed("S6")
                    add_one_point_if_needed("V5")
                    break

            if turn_off_scoring_board("S8"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S9(graph):
        """
        S9: Let/Make/Help/Watch introducer
        (also needs a dependent verb, according to the examples)
        """
        targets = {"let", "make", "help", "watch"}
        all_edges = graph.edges()

        for dep, head in all_edges.items():
            if dep != 1:
                continue

            if graph.node[dep]["word"] not in targets:
                continue

            target_head = dep

            for test_dep, test_head in all_edges.items():
                if test_head != target_head:
                    continue

                if graph.node[test_dep]["pos"] == "v":
                    scoring_board["S9"] += 1
                    break

            if turn_off_scoring_board("S9"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S10(graph):
        """
        S10: Adverbial conjunction (Also credit: S5)
        (conjunction excluding "and", "or", "then" -- according to examples)
        """
        exceptions = {"and", "or", "then"}

        for i in range(1, graph.n_nodes()):
            word = graph.node[i]["word"]
            pos = graph.node[i]["pos"]

            if pos == "conj" and word not in exceptions:
                scoring_board["S10"] += 1
                add_one_point_if_needed("S5")

            if turn_off_scoring_board("S10"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S11(graph):
        """
        S11: Propositional complement (Also credit S6)
        """
        if not graph.n_nodes() > 3:
            return

        subject_count = 0

        for dep, head in graph.edges().items():
            subject_count_increment = False

            if (
                graph.edge[dep][head]["rel"] == "SUBJ"
                and graph.node[dep]["word"] != _POSTCLITIC
            ):
                subject_count += 1
                subject_count_increment = True

            if subject_count_increment and subject_count > 1:
                scoring_board["S11"] += 1
                add_one_point_if_needed("S6")

            if turn_off_scoring_board("S11"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S12(graph):
        """
        S12: Conjoined sentences (except for imperatives, will usually have
        subj+predicate in each clause) (Also credit: S6, S5)
        """
        if not graph.n_nodes() > 3:
            return

        for dep, head in graph.edges().items():
            dep_word = graph.node[dep]["word"]

            if dep_word != "and":
                continue

            rel = graph.edge[dep][head]["rel"]

            if rel == "CONJ" and graph.node[head]["pos"] == "v":
                scoring_board["S12"] += 1
                add_one_point_if_needed("S6")
                add_one_point_if_needed("S5")

            if turn_off_scoring_board("S12"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S13(graph):
        """
        S13: Wh-clause (Also credit S6) (If also infinitive, credit S8 or S17)
        """
        if not graph.n_nodes() > 3:
            return

        for dep, head in graph.edges().items():
            dep_pos = graph.node[dep]["pos"]
            if not dep_pos.endswith("wh"):
                continue

            inf = False
            if dep + 1 in graph.nodes() and graph.node[dep + 1]["word"] == "INF":
                inf = True

            # we want the head of wh-word to NOT have ROOT as rel
            # (= ban a wh question)

            rel = ""
            for i in graph.edge[head].keys():
                rel = graph.edge[head][i]["rel"]
                break

            if rel != "ROOT":
                scoring_board["S13"] += 1
                add_one_point_if_needed("S6")

                if inf:
                    add_one_point_if_needed("S8")
                    add_one_point_if_needed("S17")

            if turn_off_scoring_board("S13"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S14(graph):
        """
        S14: Bitransitive predicate (Also credit S3)
        """
        if not graph.n_nodes() > 3:
            return

        dep_head_pairs_for_obj = []

        for dep, head in graph.edges().items():
            rel = graph.edge[dep][head]["rel"]

            if rel != "OBJ":
                continue

            dep_head_pairs_for_obj.append((dep, head))

        heads = [head for _, head in dep_head_pairs_for_obj]

        if len(set(heads)) < len(dep_head_pairs_for_obj):
            scoring_board["S14"] += 1
            add_one_point_if_needed("S3")

        if turn_off_scoring_board("S14"):
            pass

    # noinspection PyPep8Naming
    @test_item
    def S15(graph):
        """
        S15: Sentence with 3 or more VPs (Also credit S6)
        """
        if not graph.n_nodes() > 3:
            return

        number_of_verbs = sum(
            1 for i in range(1, graph.n_nodes()) if graph.node[i]["pos"] == "v"
        )

        if number_of_verbs > 2:
            scoring_board["S15"] += 1
            add_one_point_if_needed("S6")

        if turn_off_scoring_board("S15"):
            pass

    # noinspection PyPep8Naming
    @test_item
    def S16(graph):
        """
        S16: Relative clause, marked or unmarked (Also credit: S6)
        """
        # "search for a CMOD where the dependent is to the right of the head"
        # (from Sagae et al 2005 ACL)
        # add one criterion: "and" is not one of the intervening words

        if not graph.n_nodes() > 3:
            return

        for dep, head in graph.edges().items():
            if dep < head:
                continue

            if graph.edge[dep][head]["rel"] != "CMOD":
                continue

            and_ = False
            for i in range(head + 1, dep):  # dep > head
                if graph.node[i]["word"] == "and":
                    and_ = True
                    break

            if not and_:
                scoring_board["S16"] += 1
                add_one_point_if_needed("S6")

            if turn_off_scoring_board("S16"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S17(graph):
        """
        S17: Infinitive clause: new subject. (Also credit: S8)
        """
        if not graph.n_nodes() > 3:
            return

        # example of a hit case: "he wants me to go"
        # ("me" is the new subject for the infinitive clause)

        for dep, head in graph.edges().items():
            word = graph.node[dep]["word"]
            pos = graph.node[dep]["pos"]

            if word != "to" or pos != "inf":
                continue

            inf_verb = head  # "go" in the example
            main_verb = graph.edges()[inf_verb]  # "wants"

            # check if there's an object of "wants"
            for test_obj, test_main_verb in graph.edges().items():
                if test_main_verb != main_verb:
                    continue

                if graph.edge[test_obj][test_main_verb]["rel"] == "OBJ":
                    scoring_board["S17"] += 1
                    add_one_point_if_needed("S8")
                    break

            if turn_off_scoring_board("S17"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S18(graph):
        """
        S18: Gerund (Also credit: V7)
        """
        for i in range(1, graph.n_nodes()):
            pos = graph.node[i]["pos"]

            if pos == "n:gerund":
                scoring_board["S18"] += 1
                add_one_point_if_needed("V7")

            if turn_off_scoring_board("S18"):
                break

    # noinspection PyPep8Naming
    @test_item
    def S19(graph):
        """
        S19: Front or center-embedded subordinate clause (Also credit: S6)
        """
        # might need more work
        # for now: check if CONJ precedes two SUBJ's

        conj_position = graph.n_nodes()  # decrement if CONJ is found
        subj_position_list = []

        for dep, head in graph.edges().items():
            pos = graph.node[dep]["pos"]
            rel = graph.edge[dep][head]["rel"]

            if pos == "conj" and dep < conj_position:
                conj_position = dep

            if rel == "SUBJ":
                subj_position_list.append(dep)

        if len(subj_position_list) < 2:
            return

        if conj_position < min(subj_position_list):
            scoring_board["S19"] += 1
            add_one_point_if_needed("S6")

        if turn_off_scoring_board("S19"):
            pass

    return sum(scoring_board.values())
