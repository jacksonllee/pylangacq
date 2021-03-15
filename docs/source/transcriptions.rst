.. _transcriptions:

Transcriptions and Annotations
==============================

Conversational data formatted in CHAT provides transcriptions with rich
annotations for both linguistic and extra-linguistic information.
PyLangAcq is designed to extract data and annotations in CHAT and expose them
in Python data structures for flexible modeling work.
This page explains how PyLangAcq represents CHAT data and annotations.

CHAT Format
-----------

To see how the CHAT format translates to PyLangAcq, let's look at the very first
two utterances in Eve's data in the American English
`Brown <https://childes.talkbank.org/access/Eng-NA/Brown.html>`_
dataset on CHILDES (data file: ``Brown/Eve/010600a.cha``),
where apparently Eve demands cookies in the first utterance
and her mother responds with a question for confirmation in the second utterance:

.. skip: start

.. code-block::

    *CHI:	more cookie . [+ IMP]
    %mor:	qn|more n|cookie .
    %gra:	1|2|QUANT 2|0|INCROOT 3|2|PUNCT
    %int:	distinctive , loud
    *MOT:	you 0v more cookies ?
    %mor:	pro:per|you 0v|v qn|more n|cookie-PL ?
    %gra:	1|2|SUBJ 2|0|ROOT 3|4|QUANT 4|2|OBJ 5|2|PUNCT

.. skip: end

PyLangAcq handles CHAT data by paying attention to the following:

* **Participants:**
  The two participants are ``CHI`` and ``MOT``.
  In CHILDES, it is customary to denote the target child (i.e., Eve in this example)
  by ``CHI`` and the child's mother by ``MOT``.
  The asterisk ``*`` that comes just before the participant code signals
  a transcription line. Each utterance must begin with the transcription line.

* **Transcriptions:**
  The two transcription lines are ``more cookie . [+ IMP]`` from Eve
  and ``you 0v more cookies ?`` from her mother.
  The transcriptions are word-segmented by spaces
  (even for languages that don't have such orthographic conventions as English does).
  Punctuation marks are also treated as "words".
  Annotations such as ``[+ IMP]`` and ``0v`` here can be found in transcriptions.

* **Dependent tiers:**
  Between one transcription line and the next one, there are often what's known
  as dependent tiers, signed by ``%``,
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
  (including punctuation marks) in the transcription line;
  annotations in the transcription line are ignored.
  In each item of ``%mor``, the part-of-speech tag is on the left of the pipe ``|``,
  e.g., ``qn`` for a nominal quantifier in ``qn|more`` aligned to ``more`` in Eve's line.
  Inflectional and derivational information is on the right of ``|``,
  e.g., ``cookie-PL`` for the plural form of "cookie" in ``n|cookie-PL``
  aligned to ``cookies`` in Eve's mother's line.

* **The %gra tier:**
  CHAT represents grammatical relations in terms of heads and dependents in
  dependency grammar.
  Every item on the ``%gra`` tier corresponds one-to-one to the segmented words
  in the transcription (and therefore one-to-one to the ``%mor`` items as well).
  In Eve's mother's ``%gra``, ``3|4|QUANT`` means ``more`` at position 3 of the utterance
  is a dependent of the word ``cookies`` at position 4 as the head,
  and that the relation is one of quantification.

* **Other tiers:**
  Apart from ``%mor`` and ``%gra``, other dependent tiers may appear in CHAT data files.
  Some of them contain more linguistic information, e.g., ``%int`` for intonation
  in Eve's utterance here, and others contain contextual information about the
  utterance or recording session.
  Many of these tiers are used only as needed (``%int`` not used in Eve's mother's
  utterance in this example).


Once you have a :class:`~pylangacq.chat.Reader` object with CHAT data,
several methods are available for accessing the transcriptions and annotations.
Which method suits your need best depends on which level of information you need.
The following sections introduce these :class:`~pylangacq.chat.Reader` methods,
using a reader created by :func:`~pylangacq.Reader.from_strs` with the two CHAT
utterances between Eve and her mother we've looked at.

.. code-block:: python

    >>> import pylangacq
    >>> data = """
    ...     *CHI:   more cookie . [+ IMP]
    ...     %mor:   qn|more n|cookie .
    ...     %gra:   1|2|QUANT 2|0|INCROOT 3|2|PUNCT
    ...     %int:   distinctive , loud
    ...     *MOT:   you 0v more cookies ?
    ...     %mor:   pro:per|you 0v|v qn|more n|cookie-PL ?
    ...     %gra:   1|2|SUBJ 2|0|ROOT 3|4|QUANT 4|2|OBJ 5|2|PUNCT
    ... """
    >>> reader = pylangacq.Reader.from_strs([data])


Words
-----

The :class:`~pylangacq.chat.Reader` method :func:`~pylangacq.Reader.words`
returns the transcriptions as segmented words.
Calling :func:`~pylangacq.Reader.words` with no arguments gives a
flat list of the words:

.. code-block:: python

    >>> reader.words()
    ['more', 'cookie', '.', 'you', '0v', 'more', 'cookies', '?']


Output by Utterances or Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To preserve the utterance-level structure, pass in ``by_utterances=True``
so that an inner list is created around the words from each utterance:

.. code-block:: python

    >>> reader.words(by_utterances=True)
    [['more', 'cookie', '.'],
     ['you', '0v', 'more', 'cookies', '?']]

Because this example reader was created by a single in-memory string above,
internally the string was treated as if it were one single "file".
If the reader had data from multiple CHAT data files (or strings),
you might need the file-level structure in order to distinguish data from one file
to another.
Compared to the code snippet just above,
adding ``by_files=True`` captures the two utterances (= two lists of strings)
in an inner list, before the outermost list wraps up all the data:

.. code-block:: python

    >>> reader.words(by_utterances=True, by_files=True)
    [[['more', 'cookie', '.'],
      ['you', '0v', 'more', 'cookies', '?']]]


Filter by Participants
^^^^^^^^^^^^^^^^^^^^^^

Besides controlling the output for its structure,
you can also specify which participants' data to return.
The optional arguments ``participants`` and ``exclude`` are available for this purpose.
``participants`` takes a string (e.g., ``"CHI"``) or an iterable of strings
(e.g., ``{"CHI", "MOT"}``) to include only the specified participants in the output.
If specifying who to exclude is easier, use ``exclude`` instead.

.. code-block:: python

    >>> reader.words(participants="CHI", by_utterances=True)
    [['more', 'cookie', '.']]
    >>> reader.words(exclude="MOT", by_utterances=True)
    [['more', 'cookie', '.']]

Examples of use cases:

* ``participants="CHI"`` for child speech
* ``exclude="CHI"`` for child-directed speech
* ``participants={"CHI", "MOT", "FAT"}`` for parent-child interactions

Tokens
------

Beyond the transcriptions from :func:`~pylangacq.Reader.words`,
:func:`~pylangacq.Reader.tokens` gives you the word-based
annotations from the CHAT data.

.. code-block:: python

    >>> eve_tokens = reader.tokens(participants="CHI")
    >>> eve_tokens
    [Token(word='more', pos='qn', mor='more', gra=Gra(dep=1, head=2, rel='QUANT')),
     Token(word='cookie', pos='n', mor='cookie', gra=Gra(dep=2, head=0, rel='INCROOT')),
     Token(word='.', pos='.', mor='', gra=Gra(dep=3, head=2, rel='PUNCT'))]

:func:`~pylangacq.Reader.tokens` has the same optional arguments
``participants``, ``exclude``, ``by_utterances``, and ``by_files``
as :func:`~pylangacq.Reader.words` does.

While :func:`~pylangacq.Reader.words` represents a word by the built-in string type,
:func:`~pylangacq.Reader.tokens` bundles the ``%mor`` and ``%gra`` annotations
of a word into a :class:`~pylangacq.objects.Token` object.
A :class:`~pylangacq.objects.Token`'s information can be accessed via its attributes
``word``, ``pos``, ``mor``, and ``gra``:

.. code-block:: python

    >>> for token in eve_tokens:
    ...     print("word:", token.word)
    ...     print("part-of-speech tag:", token.pos)
    ...     print("morphological information:", token.mor)
    ...     print("grammatical relation:", token.gra)
    ...
    word: more
    part-of-speech tag: qn
    morphological information: more
    grammatical relation: Gra(dep=1, head=2, rel='QUANT')
    word: cookie
    part-of-speech tag: n
    morphological information: cookie
    grammatical relation: Gra(dep=2, head=0, rel='INCROOT')
    word: .
    part-of-speech tag: .
    morphological information:
    grammatical relation: Gra(dep=3, head=2, rel='PUNCT')

A grammatical relation is further represented by a :class:`~pylangacq.objects.Gra` object,
with the attributes
``dep`` (the position of the dependent, i.e., the word itself, in the utterance),
``head`` (head's position),
and ``rel`` (relation).


Utterances
----------

The :func:`~pylangacq.Reader.utterances` method gives you information
beyond :func:`~pylangacq.Reader.tokens`:

.. code-block:: python

    >>> reader.utterances(participants="CHI")
    [Utterance(participant='CHI',
               tokens=[Token(word='more', pos='qn', mor='more', gra=Gra(dep=1, head=2, rel='QUANT')),
                       Token(word='cookie', pos='n', mor='cookie', gra=Gra(dep=2, head=0, rel='INCROOT')),
                       Token(word='.', pos='.', mor='', gra=Gra(dep=3, head=2, rel='PUNCT'))],
               time_marks=None,
               tiers={'CHI': 'more cookie . [+ IMP]',
                      '%mor': 'qn|more n|cookie .',
                      '%gra': '1|2|QUANT 2|0|INCROOT 3|2|PUNCT',
                      '%int': 'distinctive , loud'})]

:func:`~pylangacq.Reader.utterances` has the same optional arguments
``participants``, ``exclude``, and ``by_files``
as :func:`~pylangacq.Reader.words` and :func:`~pylangacq.Reader.tokens` do.

Each utterance from :func:`~pylangacq.Reader.utterances` is
an :class:`~pylangacq.objects.Utterance` object,
which has the attributes
``participant``, ``tokens``, ``time_marks``, and ``tiers``
as shown in the code snippet just above.
Accessing CHAT data using :func:`~pylangacq.Reader.utterances`
is useful when you need to, say, tie participant information to
the transcriptions and/or annotations.


Time Marks
^^^^^^^^^^

Many of the more recent CHILDES datasets (especially starting from the 1990s)
come with digitized audio and video data associated with the text-based CHAT data files.
In these datasets, an utterance in the CHAT file has time marks to indicate
its start and end time (in milliseconds) in the corresponding audio and/or video data.
If the information is available, the ``time_marks`` attribute of an
:class:`~pylangacq.objects.Utterance` object is a tuple of two integers,
e.g., ``(0, 1073)``, for ``·0_1073·`` found at the end of the CHAT transcription line.


Tiers
^^^^^

You may sometimes need the original, unparsed transcription lines,
because they contain information, e.g., annotations for pauses, that is dropped
when :class:`~pylangacq.objects.Token` objects are constructed
using the cleaned-up words aligned with ``%mor`` and ``%gra``.
Or you may need access to the other ``%`` tiers not readily handled by PyLangAcq,
e.g., ``%int`` for intonation in the Eve example above.
In these cases, the ``tiers`` attribute of the :class:`~pylangacq.objects.Utterance` object
gives your a dictionary of all the original tiers of the utterance
for your custom needs.
