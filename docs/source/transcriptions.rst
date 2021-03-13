.. _transcriptions:

After the headers come the transcriptions. All transcriptions are signaled by
``*`` at the beginning of the line::

    *Code1: good morning .

``*`` is immediately followed by the participant code (e.g., ``Code1``), and then
by a colon ``:`` and a space (or tab). Then the transcribed line follows.

For research purposes, many CHAT transcripts have additional tiers signaled by
``%mor`` (for morphological information such as part-of-speech tag and lemma),
``%gra`` (for dependency and grammatical relations), and other ``%`` tiers.
Much of what PyLangAcq can do relies on the annotations in these tiers with
rich linguistic information.

Transcriptions and Annotations
==============================

This page introduces the data methods of ``Reader`` objects for transcriptions
and annotations.
For metadata access, see :ref:`metadata`.
For details of the ``Reader`` class, see :ref:`reader_api`.

* :ref:`cds`
* :ref:`word`
* :ref:`utterances`
* :ref:`transcriptions_advanced`


.. _cds:

Child speech versus child directed speech
-----------------------------------------

The distinction between child speech and child directed speech is important in
language acquisition research. Many data and metadata access methods in
PyLangAcq make this distinction possible by two optional arguments:
*participant* and *exclude*.
The *participant* parameter accepts a string
of a participant code (e.g., ``'CHI'``, ``'MOT'``) or a sequence of
participant codes (e.g., the set ``{'CHI', 'MOT'}`` to include both
participants).
Similarly, the *exclude* parameter can be either a string or a sequence of
strings, for excluding the specified participant codes.

To get child speech, set *participant* as ``'CHI'``.
To get child directed speech, set *exclude* as ``'CHI'`` to
exclude all participant codes except ``'CHI'``. Examples:

.. code-block:: python

    >>> import pylangacq as pla
    >>> eve = pla.read_chat('Brown/Eve/*.cha')
    >>> eve.number_of_utterances()  # default: include all participants
    26979
    >>> eve.number_of_utterances(participant='CHI')  # only the target child, for child speech
    12167
    >>> eve.number_of_utterances(exclude='CHI')  # excludes the target child, for child-directed speech
    14812

Most methods default *participant* to be all participants, like
``number_of_utterances()`` just illustrated above
(as well as all methods in :ref:`utterances` below).
Certain methods, such as
``age()`` and developmental measures,
are most often concerned with the target child only, and therefore
have *participant* set to be ``'CHI'`` instead by default.

To check if a method has the optional argument *participant*,
please see the complete
list of methods for the ``Reader`` class in :doc:`chat`.

.. _word:

The representation of "words"
-----------------------------

The representation of "words" in PyLangAcq comes in two flavors
(similar to NLTK):

1. The "simple" representation as a **string**,
   which is what appears as a word token in a transcription line
   starting with ``*`` in the CHAT transcript.

2. The "tagged" representation as a **tuple** of (*word*, *pos*, *mor*, *rel*),
   which contains information from the transcription line and its ``%``-tiers:

   *word* (str) -- word token string

   *pos* (str) -- part-of-speech tag

   *mor* (str) -- morphology for lemma and inflectional information, if any

   *rel* (tuple(int, int, str)) -- dependency and grammatical relation

To illustrate, let us consider the following CHAT utterance with its ``%mor``
and ``%gra`` tiers (extracted from ``eve01.cha``)::

    *MOT: but I thought you wanted me to turn it .
    %mor: conj|but pro:sub|I v|think&PAST pro|you v|want-PAST pro:obj|me inf|to v|turn pro|it .
    %gra: 1|3|LINK 2|3|SUBJ 3|0|ROOT 4|3|OBJ 5|3|JCT 6|5|POBJ 7|8|INF 8|3|XCOMP 9|8|OBJ 10|3|PUNCT


The list of "simple" words from this utterance are the list of word token
strings:

.. code-block:: python

    ['but', 'I', 'thought', 'you', 'wanted', 'me', 'to', 'turn', 'it', '.']

The list of "tagged" words from this utterance are a list of 4-tuples:

.. code-block:: python

    [('but', 'CONJ', 'but', (1, 3, 'LINK')),
     ('I', 'PRO:SUB', 'I', (2, 3, 'SUBJ')),
     ('thought', 'V', 'think&PAST', (3, 5, 'CJCT')),
     ('you', 'PRO:PER', 'you', (4, 5, 'SUBJ')),
     ('wanted', 'V', 'want-PAST', (5, 0, 'ROOT')),
     ('me', 'PRO:OBJ', 'me', (6, 5, 'OBJ')),
     ('to', 'INF', 'to', (7, 8, 'INF')),
     ('turn', 'V', 'turn', (8, 5, 'XCOMP')),
     ('it', 'PRO:PER', 'it', (9, 8, 'OBJ')),
     ('.', '.', '', (10, 5, 'PUNCT')),
    ]

The distinction of "simple" versus "tagged" words is reflected in the data
access methods introduced in :ref:`utterances` below.


.. _utterances:

Utterances
----------

To access the utterances in a ``Reader`` object, various methods are available:

=========================  ==================================================  ============================================================
Method                     Return type                                         Return object
=========================  ==================================================  ============================================================
``words()``                list of str                                         list of word strings
``tagged_words()``         list of (str, str, str, (int, int, str))            list of (*word*, *pos*, *mor*, *rel*)
``sents()``                list of [list of str]                               list of utterances as lists of word strings
``tagged_sents()``         list of [list of (str, str, str, (int, int, str))]  list of utterances as lists of (*word*, *pos*, *mor*, *rel*)
``utterances()``           list of (str, str)                                  list of (participant code, utterance)
``part_of_speech_tags()``  set of str                                          set of part-of-speech tags
=========================  ==================================================  ============================================================

.. code-block:: python

    >>> from pprint import pprint
    >>> import pylangacq as pla
    >>> eve = pla.read_chat('Brown/Eve/*.cha')
    >>> len(eve.words())  # total number of words in Eve's data
    119972
    >>> eve.words()[:5]  # first five words
    ['more', 'cookie', '.', 'you', '0v']
    >>> eve.tagged_words()[:2]  # first two tagged words
    [('more', 'QN', 'more', (1, 2, 'QUANT')), ('cookie', 'N', 'cookie', (2, 0, 'INCROOT'))]
    >>> eve.sents()[:2]  # first two sentences
    [['more', 'cookie', '.'], ['you', '0v', 'more', 'cookies', '?']]
    >>> pprint(eve.tagged_sents()[:2])  # first two tagged sentences
    [[('more', 'QN', 'more', (1, 2, 'QUANT')),
      ('cookie', 'N', 'cookie', (2, 0, 'INCROOT')),
      ('.', '.', '', (3, 2, 'PUNCT'))],
     [('you', 'PRO:PER', 'you', (1, 2, 'SUBJ')),
      ('0v', '0V', 'v', (2, 0, 'ROOT')),
      ('more', 'QN', 'more', (3, 4, 'QUANT')),
      ('cookies', 'N', 'cookie-PL', (4, 2, 'OBJ')),
      ('?', '?', '', (5, 2, 'PUNCT'))]]
    >>> pprint(eve.utterances()[:5])  # first five utterances (compare this output with "sents" above)
    [('CHI', 'more cookie .'),
     ('MOT', 'you 0v more cookies ?'),
     ('MOT', 'how_about another graham+cracker ?'),
     ('MOT', 'would that do just as_well ?'),
     ('MOT', 'here .')]
    >>> len(eve.part_of_speech_tags())  # total number of distinct part-of-speech tags
    62

The terminology of "words" and "sents" (= sentences, equivalent to utterances
here) follows NLTK, and so does "tagged" as explained in :ref:`word` above.

All the "words" and "sents" methods respect the order by which the elements
appear in the individual CHAT transcripts, which in turn are ordered
alphabetically by filenames.

All of these data access methods have the optional parameter ``by_files`` for
whether a return object X or dict(filename: X) is desired;
see :ref:`reader_properties`.

.. _transcriptions_advanced:

Advanced usage
--------------

The data access methods introduced above expose the CHAT transcriptions and
annotations with intuitive Python data structures. This allows flexible
strategies in all kinds of research involving CHAT data files.
PyLangAcq also provides additional functionalities built on top of these
methods, and they are described in other parts of the
documentation:

* :ref:`devmeasures`
* :ref:`freq`
