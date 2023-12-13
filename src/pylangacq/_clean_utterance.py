import re


_REGEX_DROP = (
    re.compile(r"\[= [^\[]+?\]"),
    re.compile(r"\[x \d+?\]"),
    re.compile(r"\[\+ [^\[]+?\]"),
    re.compile(r"\[\* [^\[]+?\]"),
    re.compile(r"\[=\? [^\[]+?\]"),
    re.compile(r"\[=! [^\[]+?\]"),
    re.compile(r"\[% [^\[]+?\]"),
    re.compile(r"\[- [^\[]+?\]"),
    re.compile(r"\[\^ [^\[]+?\]"),
    re.compile(r"[^]+?"),
    re.compile(r"\[<\d?\]"),
    re.compile(r"\[>\d?\]"),
    re.compile(r"\((\d+?:)?\d+?\.?\d*?\)"),
    re.compile(r"\[%act: [^\[]+?\]"),
)

_REGEX_REPLACE = (
    (re.compile(r"[^\[\./!]\?"), " ? "),
    (re.compile(r"\(\.\)"), " (.) "),
    (re.compile(r"([a-z])\.\Z"), r"\1 ."),
)

_REPLACEE_REPLACER = (
    ("[?]", " "),
    ("[!]", " "),
    ("[!!]", " "),
    ("[^c]", " "),
    ("‹", " "),
    ("›", " "),
    ("⌈", ""),
    ("⌉", ""),
    ("⌊", ""),
    ("⌋", ""),
    ("[*] [/", " [/"),
    ("] [*]", "] "),
    ("[*]", " "),
    ("[//] [//]", "[//]"),
    ("[/] [//]", "[//]"),
    ("[/?] [/]", "[//]"),
    ("[//] [/]", "[/]"),
    ("<", " < "),
    ("+ <", "+<"),
    (">", " > "),
    ("[", " ["),
    ("]", "] "),
    ("“", " “ "),
    ("”", " ” "),
    (",", " , "),  # works together with next line
    ("+ ,", "+,"),
)

_REGEX_SKIP_EXTRACT = (
    # xxx [:: zzz] or < xxx yyy > [:: zzz]
    (re.compile(r"(<[^>]+?>) \[:: ([^\]]+?)\]"), r"\1"),
    (re.compile(r"(\S+?) \[:: ([^\]]+?)\]"), r"\1"),
    # xxx [: zzz] or < xxx yyy > [: zzz]
    (re.compile(r"(<[^>]+?>) \[: ([^\]]+?)\]"), r"<\2>"),
    (re.compile(r"(\S+?) \[: ([^\]]+?)\]"), r"<\2>"),
)

_REGEX_DROP_AFTER_SKIP_EXTRACT = (
    # [///]
    re.compile(r"\S+? \[///\]"),
    # [//]
    re.compile(r"\S+? \[//\]"),
    # [/]
    re.compile(r"\S+? \[/\]"),
    # [/?]
    re.compile(r"\S+? \[/\?\]"),
    # [/-]
    re.compile(r"\S+? \[/-\]"),
)

_REGEX_CLEAN_WORD = (
    re.compile(r"\A<"),
    re.compile(r">\Z"),
    re.compile(r"\]\Z"),
)


def _skip_extract(utterance, regex, replacee) -> str:
    match = regex.search(utterance)
    while match:
        utterance = regex.sub(replacee, utterance)
        match = regex.search(utterance)
    else:
        return utterance


def _find_paren(utterance, check, target, opposite, direction) -> int:
    s = utterance[:check]
    if direction == "left":
        indices = range(len(s) - 1, -1, -1)
    elif direction == "right":
        indices = range(len(s))
    else:
        raise ValueError(f"direction is either left or right: {direction}")

    signal = 1
    for i in indices:
        char = s[i]
        if char == opposite:
            signal += 1
        elif char == target:
            signal -= 1
        if signal == 0:
            return i
    else:
        raise ValueError(
            "no matching paren: "
            f"{utterance} | {check} | {target} | {opposite} | {direction}"
        )


def _drop(utterance, test, target_paren, opposite_paren, paren_direction):
    check = utterance.find(test)
    if check != -1:
        paren_i = _find_paren(
            utterance, check, target_paren, opposite_paren, paren_direction
        )
        utterance = f"{utterance[: paren_i]} {utterance[check + len(test):]}"
        utterance = " ".join(utterance.split())
    return utterance


def _clean_utterance(utterance: str) -> str:
    # Remove unwanted scope elements (only the very certain cases)
    # [= whatever] for explanations
    # [x how_many_times] for collapses
    # [+ whatever] for actions etc
    # [* whatever] for error coding
    # [=? whatever] for uncertain transcriptions
    # [=! whatever] for actions etc
    # [% whatever] for random noises?
    # [- language_name] for using a non-dominant language
    # [^ whatever] for complex local events
    # whatever for audio/video time stamps? the  character is 0x15
    # [<] and [>] for overlapping, including [<1], [>2] etc with numbers
    # (2.), (3.5) etc for pauses
    # [%act: whatever] for actions etc

    # [?] for best guess
    # ‹ and › used in conjunction with [?]
    # [!] for stressing

    # "[*] [/" replaced by "[/"
    # "] [*]" replaced by "]"

    # Pad elements with spaces to avoid human transcription errors
    # If utterance has these delimiters: [ ]
    # then pad them with extra spaces to avoid errors in transcriptions
    # like "movement[?]" (--> "movement [?]")
    #
    # If utterance has:
    #     < > (left and right angle brackets), excluding "+<" (lazy overlap)
    #     “ (beginning quote)
    #     ” (ending quote)
    #     , (comma)
    #     ? (question mark)
    #     (.) (short pause)
    # then pad them with extra spaces.

    for regex in _REGEX_DROP:
        utterance = regex.sub("", utterance)

    for replacee, replacer in _REPLACEE_REPLACER:
        utterance = utterance.replace(replacee, replacer)
    # Remove extra spaces
    utterance = " ".join(utterance.split())

    for regex, replacee in _REGEX_REPLACE:
        utterance = regex.sub(replacee, utterance)
    utterance = " ".join(utterance.split())

    # Step 3:
    # Handle [/], [//], [///], [/?] for repetitions/reformulation
    #        [: xx] or [:: xx] for errors
    #
    # Strategies:
    # 1. For "z [:: x]" or "<y z> [:: x]", keep "z" or "y z" and discard the rest.
    # 2. For "z [: x]" or "<y z> [: x]", keep "x" and discard the rest.
    # 3. Discard:
    #    "xx [///]", "<xx yy> [///]",
    #    "xx [//]", "<xx yy> [//]",
    #    "xx [/]", "<xx yy> [/]"

    for regex, replacee in _REGEX_SKIP_EXTRACT:
        utterance = _skip_extract(utterance, regex, replacee)
        utterance = " ".join(utterance.split())

    current = utterance
    while True:
        utterance = _drop(utterance, "> [///]", "<", ">", "left")
        utterance = _drop(utterance, "> [//]", "<", ">", "left")
        utterance = _drop(utterance, "> [/]", "<", ">", "left")
        utterance = _drop(utterance, "> [/?]", "<", ">", "left")
        utterance = _drop(utterance, "> [/-]", "<", ">", "left")
        utterance = " ".join(utterance.split())
        if utterance == current:
            break
        else:
            current = utterance

    for regex in _REGEX_DROP_AFTER_SKIP_EXTRACT:
        utterance = regex.sub("", utterance)
        utterance = " ".join(utterance.split())

    # Step 4: Remove unwanted symbols
    for replacee, replacer in (("“", ""), ("”", "")):
        utterance = utterance.replace(replacee, replacer)

    utterance = " ".join(utterance.split())

    # Step 5: Split utterance by spaces and determine whether to keep items.

    escape_prefixes = {
        "[?",
        "[/",
        "[<",
        "[>",
        "[:",
        "[!",
        "[*",
        '+"',
        "+,",
        "<&",
        "&",  # drop this for PhonBank later?
    }
    escape_suffixes = {"↫xxx"}
    escape_words = {
        "0",
        "++",
        "+<",
        "+^",
        "(.)",
        "(..)",
        "(...)",
        ":",
        ";",
        ";;",
        "<",
        ">",
        # Drop the following for PhonBank later?
        "xx",
        "yy",
        "xxx",
        "yyy",
        "www",
        "www:",
        "xxx:",
        "xxx;",
        "xxx;;",
        "xxx→",
        "xxx↑",
        "xxx@si",
        "yyy:",
        "→",
    }
    keep_prefixes = {'+"/', "+,/", '+".'}

    words = utterance.split()
    new_words = []

    for word in words:
        # remove beginning <
        # remove final >
        # remove final ]
        for regex in _REGEX_CLEAN_WORD:
            word = regex.sub("", word)

        if any(word.startswith(k) for k in keep_prefixes):
            new_words.append(word)
            continue

        if (
            word not in escape_words
            and not any(word.startswith(e) for e in escape_prefixes)
            and not any(word.endswith(e) for e in escape_suffixes)
        ):
            new_words.append(word)

    return " ".join(new_words).strip()
