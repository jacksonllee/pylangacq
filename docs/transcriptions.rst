.. _transcriptions:

Transcriptions and Annotations
==============================

Conversational data formatted in CHAT provides transcriptions with rich
annotations for both linguistic and extra-linguistic information.
PyLangAcq is designed to extract data and annotations in CHAT and expose them
in Python data structures for flexible data analyses and modeling work.
This page explains how PyLangAcq represents CHAT data and annotations.

CHAT Format
-----------

To see how the CHAT format translates to PyLangAcq, let's look at the very first
two utterances in Eve's data in the American English
`Brown <https://childes.talkbank.org/access/Eng-NA/Brown.html>`_
dataset on CHILDES (data file: ``Brown/Eve/010600a.cha``),
where apparently Eve demands cookies in the first utterance
and her mother responds with a question for confirmation in the second utterance:

.. code-block::

    *CHI:	more cookie . [+ IMP]
    %mor:	adj|more-Cmp-S1 noun|cookie .
    %gra:	1|2|AMOD 2|2|ROOT 3|2|PUNCT
    %int:	distinctive , loud
    *MOT:	you 0v more cookies ?
    %mor:	pron|you-Prs-Acc-S2 adj|more-Cmp-S1 noun|cookie-Plur ?
    %gra:	1|3|NSUBJ 2|3|AMOD 3|3|ROOT 4|3|PUNCT

PyLangAcq handles CHAT data by paying attention to the following:

* **Participants:**
  The two participants are ``CHI`` and ``MOT``.
  In CHILDES, it is customary to denote the target child (i.e., Eve in this example)
  by ``CHI`` and the child's mother by ``MOT``.
  The asterisk ``*`` that comes just before the participant code signals
  a transcription line, known as the main tier in CHAT.
  Each utterance must begin with this main tier.

* **Transcriptions:**
  The two main tiers are ``more cookie . [+ IMP]`` from Eve
  and ``you 0v more cookies ?`` from her mother.
  The transcriptions are word-segmented by spaces
  (even for languages that don't have such orthographic conventions as English does).
  Punctuation marks are also treated as "words".
  Annotations such as ``[+ IMP]`` and ``0v`` here can be found in transcriptions.

* **Dependent tiers:**
  Between one utterance and the next, there are often what's known
  as dependent tiers, signaled by ``%`` and
  associated with the transcription line just immediately above;
  Eve's utterance has the dependent tiers ``%mor``
  (morphological information), ``%gra`` (grammatical relations),
  and ``%int`` (intonation),
  whereas Eve's mother's has only ``%mor`` and ``%gra``.
  Although certain dependent tiers are more standardized and more commonly found
  in CHILDES datasets (especially ``%mor`` and ``%gra``),
  none of the dependent tiers are obligatory in a CHAT utterance.

* **The %mor tier:**
  The morphological information aligns one-to-one to the segmented words
  (including punctuation marks) in the main tier.;
  Annotations in the main tier are ignored.
  In each item of ``%mor``, the part-of-speech tag is on the left of the pipe ``|``,
  e.g., ``adj`` for an adjective in ``adj|more-Cmp-S1`` aligned to ``more`` in Eve's utterance.
  Inflectional and derivational information is on the right of ``|``,
  e.g., ``you-Prs-Acc-S2`` for the second-person, singular, accusative, personal pronoun
  in ``pron|you-Prs-Acc-S2`` aligned to ``you`` in Eve's mother's line.

* **The %gra tier:**
  CHAT represents grammatical relations in terms of heads and dependents in
  dependency grammar.
  Every item on the ``%gra`` tier corresponds one-to-one to the segmented words
  in the transcription (and therefore one-to-one to the ``%mor`` items as well).
  In Eve's mother's ``%gra``, ``2|3|AMOD`` means ``more`` at position 2 of the utterance
  is a dependent of the word ``cookies`` at position 3 as the head,
  and that the relation is one of adjectival modification.

* **Other tiers:**
  Apart from ``%mor`` and ``%gra``, other dependent tiers may appear in CHAT data files.
  Some of them contain more linguistic information, e.g., ``%int`` for intonation
  in Eve's utterance here, and others contain contextual information about the
  utterance or recording session.
  Many of these tiers are used only as needed (``%int`` not used in Eve's mother's
  utterance in this example).

Once you have a :class:`~pylangacq.CHAT` object,
several methods are available for accessing the transcriptions and annotations.
Which method suits your need best depends on which level of information you need.
The following sections introduce these :class:`~pylangacq.CHAT` methods.
As an example, let's work with the
`Brown <https://childes.talkbank.org/access/Eng-NA/Brown.html>`_
dataset of American English on CHILDES
(see :ref:`read` for how to download and read this dataset):

.. code-block:: python

    import pylangacq
    brown = pylangacq.read_chat("path/to/your/local/Brown.zip")


Filtering by File
-----------------

The Brown dataset contains data for the three children Adam, Eve, and Sarah.
Let's first take a look at how the Brown dataset is structure,
because we need to separate the children's data for analysis:

.. code-block:: python

    brown.n_files
    # 214
    brown.file_paths
    # ['Brown/Adam/020304.cha',
    #  'Brown/Adam/020318.cha',
    #  ...
    #  'Brown/Eve/010600a.cha',
    #  'Brown/Eve/010600b.cha',
    #  ...
    #  'Brown/Sarah/020305.cha',
    #  'Brown/Sarah/020307.cha',
    #  ...]

The three children's data is organized in subdirectories under their respective name.
The :meth:`~pylangacq.CHAT.filter` method can be used to create a new :class:`~pylangacq.CHAT`
from the data matching a subdirectory path:

.. code-block:: python

    eve = brown.filter(files="Eve")
    eve.n_files
    # 20
    eve.head()
    # *CHI:  more             cookie       .
    # %mor:  adj|more-Cmp-S1  noun|cookie  .
    # %gra:  1|2|AMOD         2|2|ROOT     3|2|PUNCT
    # %int:  distinctive , loud

    # *MOT:  you                  more             cookies           ?
    # %mor:  pron|you-Prs-Acc-S2  adj|more-Cmp-S1  noun|cookie-Plur  ?
    # %gra:  1|3|NSUBJ            2|3|AMOD         3|3|ROOT          4|3|PUNCT

    # *MOT:  how_about      another              graham        cracker       ?
    # %mor:  intj|howabout  det|another-Def-Ind  noun|graham   noun|cracker  ?
    # %gra:  1|4|DISCOURSE  2|4|DET              3|4|COMPOUND  4|4|ROOT      5|4|PUNCT

    # *MOT:  would            that           do             just        as          well       ?
    # %mor:  aux|would-Fin-S  pron|that-Dem  verb|do-Inf-S  adv|just    adv|as      adv|well   ?
    # %gra:  1|3|AUX          2|3|NSUBJ      3|6|ROOT       4|5|ADVMOD  5|3|ADVMOD  6|5|FIXED  7|3|PUNCT

    # *MOT:  here      .
    # %mor:  adv|here  .
    # %gra:  1|1|ROOT  2|1|PUNCT

The string ``"Eve"`` appears in the file paths for Eve's data,
which is what we've passed in to the ``files`` keyword argument of :meth:`~pylangacq.CHAT.filter`
for filtering. There are 20 CHAT data files for Eve in Brown.


Filtering by Participant
------------------------

To filter by participant, use the ``participants`` keyword argument.
Let's further filter ``eve`` into child speech and child-directed speech:

.. code-block:: python

    eve_chi = eve.filter(participants="CHI")  # child speech
    eve_chi.head()
    # *CHI:  more             cookie       .
    # %mor:  adj|more-Cmp-S1  noun|cookie  .
    # %gra:  1|2|AMOD         2|2|ROOT     3|2|PUNCT
    # %int:  distinctive , loud

    # *CHI:  more             cookie       .
    # %mor:  adj|more-Cmp-S1  noun|cookie  .
    # %gra:  1|2|AMOD         2|2|ROOT     3|2|PUNCT
    # %int:  distinctive , loud

    # *CHI:  more             juice       ?
    # %mor:  adj|more-Cmp-S1  noun|juice  ?
    # %gra:  1|2|AMOD         2|2|ROOT    3|2|PUNCT

    # *CHI:  Fraser        .
    # %mor:  propn|Fraser  .
    # %gra:  1|1|ROOT      2|1|PUNCT
    # %com:  pronounces Fraser as fr&jdij .

    # *CHI:  Fraser        .
    # %mor:  propn|Fraser  .
    # %gra:  1|1|ROOT      2|1|PUNCT


    eve_cds = eve.filter(participants="^(?!CHI$)")  # child-directed speech, regex ^(?!CHI$) for "not CHI"
    eve_cds.head()
    # *MOT:  you                  more             cookies           ?
    # %mor:  pron|you-Prs-Acc-S2  adj|more-Cmp-S1  noun|cookie-Plur  ?
    # %gra:  1|3|NSUBJ            2|3|AMOD         3|3|ROOT          4|3|PUNCT

    # *MOT:  how_about      another              graham        cracker       ?
    # %mor:  intj|howabout  det|another-Def-Ind  noun|graham   noun|cracker  ?
    # %gra:  1|4|DISCOURSE  2|4|DET              3|4|COMPOUND  4|4|ROOT      5|4|PUNCT

    # *MOT:  would            that           do             just        as          well       ?
    # %mor:  aux|would-Fin-S  pron|that-Dem  verb|do-Inf-S  adv|just    adv|as      adv|well   ?
    # %gra:  1|3|AUX          2|3|NSUBJ      3|6|ROOT       4|5|ADVMOD  5|3|ADVMOD  6|5|FIXED  7|3|PUNCT

    # *MOT:  here      .
    # %mor:  adv|here  .
    # %gra:  1|1|ROOT  2|1|PUNCT

    # *MOT:  here      you                  go                       .
    # %mor:  adv|here  pron|you-Prs-Nom-S2  verb|go-Fin-Ind-Pres-S2  .
    # %gra:  1|3|ROOT  2|3|NSUBJ            3|1|ADVCL-RELCL          4|1|PUNCT

The ``participants`` argument of :meth:`~pylangacq.CHAT.filter` supports
regex matching (which is also true for the ``files`` argument, though not illustrated here).
We've taken advantage of this capability to filter Eve's data down to
child-directed speech, by the regular expression ``"^(?!CHI$)"``
for "not CHI". 


Words
-----

The :class:`~pylangacq.CHAT` method :meth:`~pylangacq.CHAT.words`
returns the transcriptions as segmented words.

Calling :meth:`~pylangacq.CHAT.words` with no arguments gives a
flat list of all the words:

.. code-block:: python

    eve_chi.words()[:9]
    # ['more', 'cookie', '.', 'more', 'cookie', '.', 'more', 'juice', '?']
    len(eve_chi.words())
    # 44119
    eve_cds.words()[:9]
    # ['you', 'more', 'cookies', '?', 'how_about', 'another', 'graham', 'cracker', '?']
    len(eve_cds.words())
    # 76198

To preserve the utterance-level structure, pass in ``by_utterance=True``
so that an inner list is created around the words from each utterance:

.. code-block:: python

    eve_chi.words(by_utterance=True)[:5]
    # [['more', 'cookie', '.'],
    #  ['more', 'cookie', '.'],
    #  ['more', 'juice', '?'],
    #  ['Fraser', '.'],
    #  ['Fraser', '.']]
    len(eve_chi.words(by_utterance=True))
    # 12113
    eve_cds.words(by_utterance=True)[:5]
    # [['you', 'more', 'cookies', '?'],
    #  ['how_about', 'another', 'graham', 'cracker', '?'],
    #  ['would', 'that', 'do', 'just', 'as', 'well', '?'],
    #  ['here', '.'],
    #  ['here', 'you', 'go', '.']]
    len(eve_cds.words(by_utterance=True))
    # 14807

Eve's data comes from 20 CHAT data files.
To get the file-level structure, pass in ``by_file=True``.
Each inner list contains the flat words from one file:

.. code-block:: python

    eve_chi_by_file = eve_chi.words(by_file=True)
    len(eve_chi_by_file)
    # 20
    eve_chi_by_file[0][:9]
    # ['more', 'cookie', '.', 'more', 'cookie', '.', 'more', 'juice', '?']
    eve_cds_by_file = eve_cds.words(by_file=True)
    len(eve_cds_by_file)
    # 20
    eve_cds_by_file[0][:9]
    # ['you', 'more', 'cookies', '?', 'how_about', 'another', 'graham', 'cracker', '?']

Passing both ``by_utterance=True`` and ``by_file=True`` gives a list of files,
where each file is a list of utterances, and each utterance is a list of words:

.. code-block:: python

    eve_chi_both = eve_chi.words(by_utterance=True, by_file=True)
    len(eve_chi_both)
    # 20
    len(eve_chi_both[0])
    # 741
    eve_chi_both[0][:5]
    # [['more', 'cookie', '.'],
    #  ['more', 'cookie', '.'],
    #  ['more', 'juice', '?'],
    #  ['Fraser', '.'],
    #  ['Fraser', '.']]
    eve_cds_both = eve_cds.words(by_utterance=True, by_file=True)
    len(eve_cds_both)
    # 20
    len(eve_cds_both[0])
    # 847
    eve_cds_both[0][:5]
    # [['you', 'more', 'cookies', '?'],
    #  ['how_about', 'another', 'graham', 'cracker', '?'],
    #  ['would', 'that', 'do', 'just', 'as', 'well', '?'],
    #  ['here', '.'],
    #  ['here', 'you', 'go', '.']]


Tokens
------

While :meth:`~pylangacq.CHAT.words` gives you transcriptions as plain strings,
:meth:`~pylangacq.CHAT.tokens` gives you the ``%mor`` and ``%gra``
annotations bundled with each word:

.. code-block:: python

    eve_chi.tokens()[:3]
    # [Token(word='more', pos='adj', mor='more-Cmp-S1', gra=Gra(dep=1, head=2, rel='AMOD')),
    #  Token(word='cookie', pos='noun', mor='cookie', gra=Gra(dep=2, head=2, rel='ROOT')),
    #  Token(word='.', pos='', mor='.', gra=Gra(dep=3, head=2, rel='PUNCT'))]

Each element is a :class:`~pylangacq.Token` object
with the attributes ``word``, ``pos``, ``mor``, and ``gra``:

.. code-block:: python

    first_token = eve_chi.tokens()[0]
    first_token.word
    # 'more'
    first_token.pos
    # 'adj'
    first_token.mor
    # 'more-Cmp-S1'
    first_token.gra
    # Gra(dep=1, head=2, rel='AMOD')

The ``gra`` attribute is a :class:`~pylangacq.Gra` object,
with the attributes
``dep`` (the position of the word in the utterance),
``head`` (position of the head word),
and ``rel`` (the grammatical relation):

.. code-block:: python

    first_token.gra.dep
    # 1
    first_token.gra.head
    # 2
    first_token.gra.rel
    # 'AMOD'

Like :meth:`~pylangacq.CHAT.words`,
:meth:`~pylangacq.CHAT.tokens` also accepts
``by_utterance`` and ``by_file`` to organize the results
at the utterance and file level, respectively.

Clitics
^^^^^^^

In CHAT, clitics are morphemes that attach to a host word but carry their own
part-of-speech and morphological information on the ``%mor`` tier.
Postclitics are marked with ``~`` and preclitics with ``$``.
For example, the contraction *that's* is annotated as
``pro:dem|that~cop|be&3S`` -- the demonstrative pronoun *that* followed by
the postclitic copula *be*.
When PyLangAcq parses such forms, the host word's :class:`~pylangacq.Token`
receives the transcribed word (e.g., ``"that's"``), while clitic tokens
get an empty string for their ``word`` attribute but retain their ``pos``,
``mor``, and ``gra`` annotations.
This means the number of tokens in an utterance can exceed the number of words,
because each clitic produces its own :class:`~pylangacq.Token`:

.. code-block:: python

    import pylangacq

    # "that's good ." with %mor: pro:dem|that~cop|be&3S adj|good .
    chat_str = (
        "@UTF8\n@Begin\n"
        "@Participants:\tCHI Target_Child\n"
        "*CHI:\tthat's good .\n"
        "%mor:\tpro:dem|that~cop|be&3S adj|good .\n"
        "@End\n"
    )
    reader = pylangacq.CHAT.from_strs([chat_str])
    tokens = reader.tokens(by_utterance=True)[0]
    len(tokens)
    # 4 (three words, but four tokens because of the postclitic)
    tokens[0].word, tokens[0].pos
    # ("that's", 'pro:dem')
    tokens[1].word, tokens[1].pos
    # ('', 'cop')           # postclitic: empty word, but POS is retained
    tokens[2].word, tokens[2].pos
    # ('good', 'adj')
    tokens[3].word, tokens[3].pos
    # ('.', '')


Utterances
----------

The :meth:`~pylangacq.CHAT.utterances` method returns
:class:`~pylangacq.Utterance` objects that bundle together
the participant, tokens, original tiers, and time marks for each utterance:

.. code-block:: python

    eve_chi.utterances()[0]
    # Utterance(participant='CHI', tokens=[...3 tokens], time_marks=None)

Each :class:`~pylangacq.Utterance` object has the following attributes:

* ``participant`` -- the speaker code (e.g., ``'CHI'``, ``'MOT'``).
* ``tokens`` -- a list of :class:`~pylangacq.Token` objects,
  the same kind introduced in the Tokens section above.
* ``audible`` -- the audibly faithful transcription of this utterance,
  with CHAT coding conventions stripped out while preserving
  repetitions and retracings as they were heard; ``None`` for changeable headers.
* ``tiers`` -- a dictionary of the original, unparsed tier lines.
* ``time_marks`` -- a tuple of ``(start, end)`` in milliseconds, or ``None``.
* ``changeable_header`` -- a :class:`~pylangacq.ChangeableHeader` object
  if this entry is a mid-file header, or ``None`` for regular utterances.

Let's inspect these attributes on the first utterance of Eve's child speech:

.. code-block:: python

    u = eve_chi.utterances()[0]
    u.participant
    # 'CHI'
    u.tokens
    # [Token(word='more', pos='adj', mor='more-Cmp-S1', gra=Gra(dep=1, head=2, rel='AMOD')),
    #  Token(word='cookie', pos='noun', mor='cookie', gra=Gra(dep=2, head=2, rel='ROOT')),
    #  Token(word='.', pos='', mor='.', gra=Gra(dep=3, head=2, rel='PUNCT'))]
    u.tokens[0].word
    # 'more'
    u.tokens[0].pos
    # 'adj'
    u.audible
    # 'more cookie .'
    u.time_marks is None
    # True

The ``tokens`` here are exactly the same :class:`~pylangacq.Token` objects
returned by :meth:`~pylangacq.CHAT.tokens` --
each with the ``word``, ``pos``, ``mor``, and ``gra`` attributes
as described in the Tokens section above.

Like :meth:`~pylangacq.CHAT.words` and :meth:`~pylangacq.CHAT.tokens`,
:meth:`~pylangacq.CHAT.utterances` accepts ``by_file``
to organize the results at the file level:

.. code-block:: python

    len(eve_chi.utterances())  # number of utterances, in Eve's child speech data
    # 12113
    eve_chi_by_file = eve_chi.utterances(by_file=True)
    len(eve_chi_by_file)  # number of files, in Eve's child speech data
    # 20
    len(eve_chi_by_file[0])  # number of utterances in the 1st file of Eve's child speech data
    # 741


Audibly Faithful Transcription
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``audible`` attribute of an :class:`~pylangacq.Utterance` object
gives you a transcription that faithfully represents what was audibly spoken,
with CHAT coding conventions (e.g., ``[+ IMP]``) stripped out
while preserving repetitions and retracings as they were heard:

.. code-block:: python

    import pylangacq

    # Repetitions marked with [x N] are expanded:
    data1 = pylangacq.CHAT.from_strs(["*CHI:\tno [x 3] ."])
    data1.utterances()[0].audible
    # 'no no no .'

    # Retracings are kept as spoken:
    data2 = pylangacq.CHAT.from_strs(["*CHI:\tI want [/] I want cookie ."])
    data2.utterances()[0].audible
    # 'I want I want cookie .'

This transcription is useful for tasks where the goal is to model
the actual speech signal, such as automatic speech recognition (ASR)
and forced alignment, where to the extent possible the text matches what was audibly produced.
For changeable header entries, ``audible`` is ``None``.


Changeable Headers
^^^^^^^^^^^^^^^^^^

CHAT data files can contain mid-file headers marked by ``@`` in the source data,
such as ``@G``, ``@Comment``, ``@Date``, and ``@Situation``.
These "changeable headers" (as they're called in the official CHAT documentation)
signal metadata changes within a recording session
(as opposed to the file-level headers that appear at the top of a CHAT file).

When :meth:`~pylangacq.CHAT.utterances` encounters a mid-file header,
it includes it in the returned list as an :class:`~pylangacq.Utterance` object
whose ``changeable_header`` attribute is set
(while ``participant``, ``tokens``, and ``tiers`` are all ``None``):

.. code-block:: python

    eve = brown.filter(files="Eve")
    utts = eve.utterances()
    headers = [u for u in utts if u.changeable_header is not None]
    len(headers)
    # 49
    h = headers[0]
    h.changeable_header
    # <builtins.ChangeableHeader_Date object at ...>
    h.changeable_header.value
    # '17-OCT-1962'
    h.participant is None
    # True
    h.tokens is None
    # True
    h.tiers is None
    # True

You can use ``isinstance`` with :class:`~pylangacq.ChangeableHeader` variants
to classify the headers you find.
For example, to collect all dates, comments, and situations from Eve's data:

.. code-block:: python

    from pylangacq import ChangeableHeader
    found_dates = []
    found_comments = []
    found_situations = []
    for u in eve.utterances():
        if u.changeable_header is not None:
            ch = u.changeable_header
            if isinstance(ch, ChangeableHeader.Date):
                found_dates.append(ch.value)
            elif isinstance(ch, ChangeableHeader.Comment):
                found_comments.append(ch.value)
            elif isinstance(ch, ChangeableHeader.Situation):
                found_situations.append(ch.value)
    found_dates[:5]
    # ['17-OCT-1962', '31-OCT-1962', '28-NOV-1962', '10-DEC-1962', '12-DEC-1962']
    found_comments[:3]
    # ['end of episode', '15:00-16:00', '30-JAN-1963 , 10:45-11:45']
    found_situations[:2]
    # ['Eve is playing with large wooden beads. she sorts them by colors , although she often fails to use color names appropriately.',
    #  'Father is going to have apple']


Time Marks
^^^^^^^^^^

Many of the more recent CHILDES datasets (especially starting from the 1990s)
come with digitized audio and video data associated with the text-based CHAT data files.
In these datasets, an utterance in the CHAT file has time marks to indicate
its start and end time (in milliseconds) in the corresponding audio and/or video data.
If the information is available, the ``time_marks`` attribute of an
:class:`~pylangacq.Utterance` object is a tuple of two integers,
e.g., ``(0, 1073)``, for ``·0_1073·`` found at the end of the CHAT main tier.


Original Tiers
^^^^^^^^^^^^^^

You may sometimes need the original, unparsed transcription lines,
because they contain information (e.g., annotations for pauses) that is dropped
when :class:`~pylangacq.Token` objects are constructed
from the cleaned-up words aligned with ``%mor`` and ``%gra``.
Or you may need access to other ``%`` tiers,
e.g., ``%int`` for intonation or ``%com`` for comments.
The ``tiers`` attribute of an :class:`~pylangacq.Utterance` object
gives you a dictionary of all the original tiers of the utterance
for your custom needs:

.. code-block:: python

    u = eve_chi.utterances()[0]
    u.tiers
    # {'%gra': '1|2|AMOD 2|2|ROOT 3|2|PUNCT',
    #  '%int': 'distinctive , loud',
    #  'CHI': 'more cookie . [+ IMP]',
    #  '%mor': 'adj|more-Cmp-S1 noun|cookie .'}

The dictionary keys include the participant code (``'CHI'``) for the main tier
and the dependent tier names (``'%mor'``, ``'%gra'``, ``'%int'``, etc.).
Notice that the main tier retains the original transcription ``'more cookie . [+ IMP]'``,
including the ``[+ IMP]`` annotation that is not part of the parsed tokens.


.. _chat_from_utterances:

Creating a ``CHAT`` Object from ``Utterance`` Objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a list of :class:`~pylangacq.Utterance` objects
(e.g., after filtering or transforming utterances programmatically),
you can construct a new :class:`~pylangacq.CHAT` reader from them
using the :meth:`~pylangacq.CHAT.from_utterances` classmethod.
The resulting reader behaves like any other :class:`~pylangacq.CHAT` object,
so you can call :meth:`~pylangacq.CHAT.words`, :meth:`~pylangacq.CHAT.tokens`,
and other methods on it as usual:

.. code-block:: python

    eve_chi = eve.filter(participants="CHI")
    utts = eve_chi.utterances()

    # Create a new reader from the first 10 utterances
    subset = pylangacq.CHAT.from_utterances(utts[:10])
    subset.words()[:9]
    # ['more', 'cookie', '.', 'more', 'cookie', '.', 'more', 'juice', '?']
    len(subset.utterances())
    # 10

    # Round-trip: reconstructing a reader preserves all data
    reconstructed = pylangacq.CHAT.from_utterances(utts)
    reconstructed.words() == eve_chi.words()
    # True
