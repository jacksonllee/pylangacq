import re


CLITIC = "CLITIC"
ENCODING = "utf8"
TIMER_MARKER_REG = re.compile(r"\x15-?(\d+)_(\d+)-?\x15")


def clean_utterance(utterance, phon=False):
    """Filter away the CHAT-style annotations in ``utterance``.

    Parameters
    ----------
    utterance : str
        The utterance as a str
    phon : bool, optional
        whether we are handling PhonBank data; defaults to False.
        If ``True``, words like "xxx" and "yyy" won't be removed.

    Returns
    -------
    str
    """
    # Function tested with the following CHILDES datasets:
    # 1) Brent, Brown, HSLLD, Kuczaj, MacWhinney, Valian in Eng-NA-MOR
    # 2) YipMatthews in Biling
    # 3) LeeWongLeung in EastAsian/Cantonese
    # 4) CromptonPater, Goad, Inkelas, and Providence in PhonBank English

    # *** At the end of each step, apply remove_extra_spaces(). ***

    # Step 1: Remove unwanted scope elements (only the very certain cases)
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

    # print('utterance:', utterance, type(utterance))

    utterance = re.sub(r"\[= [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[x \d+?\]", "", utterance)
    utterance = re.sub(r"\[\+ [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[\* [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[=\? [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[=! [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[% [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[- [^\[]+?\]", "", utterance)
    utterance = re.sub(r"\[\^ [^\[]+?\]", "", utterance)
    utterance = re.sub(r"[^]+?", "", utterance)  # TODO: Why need this?!
    utterance = re.sub(r"\[<\d?\]", "", utterance)
    utterance = re.sub(r"\[>\d?\]", "", utterance)
    utterance = re.sub(r"\(\d+?\.?\d*?\)", "", utterance)
    utterance = re.sub(r"\[%act: [^\[]+?\]", "", utterance)

    utterance = re.sub(r"\[\?\]", "", utterance)
    utterance = re.sub(r"\[\!\]", "", utterance)
    utterance = re.sub(r"‹", "", utterance)
    utterance = re.sub(r"›", "", utterance)

    utterance = re.sub(r"\[\*\] \[/", "[/", utterance)
    utterance = re.sub(r"\] \[\*\]", "]", utterance)

    utterance = remove_extra_spaces(utterance)
    # print('step 1:', utterance)

    # Step 2: Pad elements with spaces to avoid human transcription errors
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
    #     . (period) <-- commented out at the moment
    #     (.) (short pause)
    # then pad them with extra spaces.

    utterance = re.sub(r"<", " <", utterance)
    utterance = re.sub(r"\+ <", "+<", utterance)
    utterance = re.sub(r">", "> ", utterance)
    utterance = re.sub(r"\[", " [", utterance)
    utterance = re.sub(r"\]", "] ", utterance)
    utterance = re.sub(r"“", " “ ", utterance)
    utterance = re.sub(r"”", " ” ", utterance)
    utterance = re.sub(r",", " , ", utterance)  # works together with next line
    utterance = re.sub(r"\+ ,", "+,", utterance)
    utterance = re.sub(r"[^\[\./!]\?", " ? ", utterance)
    # utterance = re.sub('[^\(\[\.\+]\.', ' . ', utterance)
    utterance = re.sub(r"\(\.\)", " (.) ", utterance)
    utterance = remove_extra_spaces(utterance)
    # print('step 2:', utterance)

    # Step 3:
    # Handle [/], [//], [///], [/?] for repetitions/reformulation
    #        [: xx] or [:: xx] for errors
    #
    # Discard "xx [/]", "<xx yy> [/]", "xx [//]", "<xx yy> [//]".
    # For "zz [: xx]" or "<yy zz> [:: xx]", keep "xx" and discard the rest.
    #
    # Strategies:
    # 1. Get all matching index pairs for angle brackets < and >.
    # 2. Delete the unwanted material inside and including these brackets
    #    plus their signaling annotations (= "[:", "[::", "[/]", "[//]").
    # 3. Delete the unwanted words on the left of the signaling annotations.

    angle_brackets_l2r_pairs = {}  # left-to-right
    for index_ in find_indices(utterance, "<"):
        counter = 1
        for i in range(index_ + 1, len(utterance)):
            if utterance[i] == "<":
                counter += 1
            elif utterance[i] == ">":
                counter -= 1

            if counter == 0:
                angle_brackets_l2r_pairs[index_] = i
                break
    angle_brackets_r2l_pairs = {v: k for k, v in angle_brackets_l2r_pairs.items()}

    index_pairs = []  # characters bounded by index pairs to be removed

    # remove ' [///]'
    triple_slash_right_indices = find_indices(utterance, r"> \[///\]")
    index_pairs += [(begin + 1, begin + 6) for begin in triple_slash_right_indices]

    # remove ' [//]'
    double_overlap_right_indices = find_indices(utterance, r"> \[//\]")
    index_pairs += [(begin + 1, begin + 5) for begin in double_overlap_right_indices]

    # remove ' [/]'
    single_overlap_right_indices = find_indices(utterance, r"> \[/\]")
    index_pairs += [(begin + 1, begin + 4) for begin in single_overlap_right_indices]

    # remove ' [/?]'
    slash_question_indices = find_indices(utterance, r"> \[/\?\]")
    index_pairs += [(begin + 1, begin + 4) for begin in slash_question_indices]

    # remove ' [::'
    double_error_right_indices = find_indices(utterance, r"> \[::")
    index_pairs += [(begin + 1, begin + 4) for begin in double_error_right_indices]

    # remove ' [:'
    single_error_right_indices = find_indices(utterance, r"> \[: ")
    index_pairs += [(begin + 1, begin + 3) for begin in single_error_right_indices]

    right_indices = (
        double_overlap_right_indices
        + single_overlap_right_indices
        + double_error_right_indices
        + single_error_right_indices
        + triple_slash_right_indices
        + slash_question_indices
    )

    index_pairs = index_pairs + [
        (angle_brackets_r2l_pairs[right], right) for right in sorted(right_indices)
    ]
    indices_to_ignore = set()
    for left, right in index_pairs:
        for i in range(left, right + 1):
            indices_to_ignore.add(i)

    new_utterance = ""
    for i in range(len(utterance)):
        if i not in indices_to_ignore:
            new_utterance += utterance[i]
    utterance = new_utterance

    utterance = re.sub(r"\S+? \[/\]", "", utterance)
    utterance = re.sub(r"\S+? \[//\]", "", utterance)
    utterance = re.sub(r"\S+? \[///\]", "", utterance)
    utterance = re.sub(r"\S+? \[/\?\]", "", utterance)

    utterance = re.sub(r"\S+? \[::", "", utterance)
    utterance = re.sub(r"\S+? \[:", "", utterance)

    utterance = remove_extra_spaces(utterance)
    # print('step 3:', utterance)

    # Step 4: Remove unwanted symbols
    utterance = re.sub(r"“", "", utterance)
    utterance = re.sub(r"”", "", utterance)

    utterance = remove_extra_spaces(utterance)

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
    }
    escape_words = {"0", "++", "+<", "+^", "(.)", "(..)", "(...)", ":", ";"}
    keep_prefixes = {'+"/', "+,/", '+".'}

    if not phon:
        escape_words.update({"xxx", "yyy", "www", "xxx:", "yyy:"})
        escape_prefixes.update({"&"})
    else:
        escape_words.update({","})
        escape_prefixes.update({"0"})

    words = utterance.split()
    new_words = []

    for word in words:
        word = re.sub(r"\A<", "", word)  # remove beginning <
        word = re.sub(r">\Z", "", word)  # remove final >
        word = re.sub(r"\]\Z", "", word)  # remove final ]

        not_an_escape_word = word not in escape_words
        no_escape_prefix = not any(word.startswith(e) for e in escape_prefixes)
        has_keep_prefix = any(word.startswith(k) for k in keep_prefixes)

        if (not_an_escape_word and no_escape_prefix) or has_keep_prefix:
            new_words.append(word)

    # print('step 5:', remove_extra_spaces(' '.join(new_words)))

    return remove_extra_spaces(" ".join(new_words))


def get_time_marker(utterance):  # TODO write tests this function
    """Get the timer marker in this utterance.

    Time marker provides the start and end times (in milliseconds)
    for a segment in a digitized video or audio file. For example:
        ·0_1073·
    '·' is ASCII CODE 21 (0x15), for NAK (Negative Acknowledgement)

    Parameters
    ----------
    utterance : str
        The raw utterance

    Returns
    -------
    tuple of (int, int)
        The start and end times (in milliseconds) for this utterance

    Notes
    -----
    If the option “multiple” is selected in the @Options field, then these '·'
    bullets may also occur within utterances. However, this function only
    returns one timer marker. (See https://talkbank.org/manuals/CHAT.pdf)
    """
    match = TIMER_MARKER_REG.search(utterance)
    if match:
        time_marker = match.groups()
        start = int(time_marker[0])
        stop = int(time_marker[1])
        return start, stop
    else:
        msg = "Utterance does not have a standard time marker: %s" % utterance
        raise ValueError(msg)


def get_participant_code(tier_marker_seq):
    """Return the participant code from a tier marker set.

    Parameters
    ----------
    tier_marker_seq : iterable of str
        A sequence of tier markers like ``{'CHI', '%mor', '%gra'}``

    Returns
    -------
    str
        A participant code, e.g., ``'CHI'``.
        Return ``None`` if no participant code is found.
    """
    for tier_marker in tier_marker_seq:
        if not tier_marker.startswith("%"):
            return tier_marker
    return None


def clean_word(word):
    """Clean the word.

    Parameters
    ----------
    word : str

    Returns
    -------
    str
    """
    new_word = (
        word.replace("(", "")
        .replace(")", "")
        .replace(":", "")
        .replace(";", "")
        .replace("+", "")
    )

    if "@" in new_word:
        new_word = new_word[: new_word.index("@")]

    if new_word.startswith("&"):
        new_word = new_word[1:]

    return new_word


def convert_date_to_tuple(date_str):
    """Convert ``date_str`` to (year, month, day).

    Parameters
    ----------
    date_str : str


    Returns
    -------
    (int, int, int)

    Examples
    --------
    >>> convert_date_to_tuple('01-FEB-2016')
    (2016, 2, 1)
    """
    try:
        day_str, month_str, year_str = date_str.split("-")
        day = int(day_str)
        year = int(year_str)

        month_to_int = {
            "JAN": 1,
            "FEB": 2,
            "MAR": 3,
            "APR": 4,
            "MAY": 5,
            "JUN": 6,
            "JUL": 7,
            "AUG": 8,
            "SEP": 9,
            "OCT": 10,
            "NOV": 11,
            "DEC": 12,
        }

        month = month_to_int[month_str]
        return year, month, day
    except ValueError:
        return None


def get_lemma_from_mor(mor):
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


def remove_extra_spaces(inputstr):
    """Remove extra spaces in *inputstr* so that there are only single spaces.

    Parameters
    ----------
    inputstr : str

    Returns
    -------
    str
    """
    while "  " in inputstr:
        inputstr = inputstr.replace("  ", " ")
    return inputstr.strip()


def find_indices(longstr, substring):
    """Find all indices of non-overlapping ``substring`` in ``longstr``.

    Parameters
    ----------
    longstr : str
    substring : str

    Returns
    -------
    list of int
        List of indices of the long string for where substring occurs
    """
    return [m.start() for m in re.finditer(substring, longstr)]
