.. _quickstart:

Quickstart
==========

This page introduces the basic functionality of PyLangAcq and points to
relevant pages of the library documentation for more advanced usage.

To start, import the package ``pylangacq`` in your Python code:

.. code-block:: python

    >>> import pylangacq

No errors? Great! Now you're ready to proceed.

Reading CHAT data
-----------------

First off, we need some CHAT data to work with.
The function ``read_chat`` asks for a data source and returns a CHAT data reader.
The data source can either be local on your computer,
or a remote source as a ZIP archive file containing `.cha` files.
A prototypical example for the latter is a dataset from CHILDES.
To illustrate, let's use Eve's data from the Brown corpus of American English:

.. code-block:: python

    >>> url = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"
    >>> eve = pylangacq.read_chat(url, "Eve")
    >>> len(eve)
    20

``eve`` is a ``Reader`` instance.
It has Eve's 20 CHAT data files all parsed and ready at your disposal.
``eve`` has various methods through which you can access different information
with Pythonic data structures.

More on :ref:`read`.

Header Information
------------------

CHAT transcript files store metadata in the header with lines beginning with ``@``.
Among other things, we can find the ages (if available from the header)
of the target child when the recordings were made:

.. code-block:: python

    >>> from pprint import pprint
    >>> pprint(eve.ages())
    [(1, 6, 0),
     (1, 6, 0),
     (1, 7, 0),
     (1, 7, 0),
     (1, 8, 0),
     (1, 9, 0),
     (1, 9, 0),
     (1, 9, 0),
     (1, 10, 0),
     (1, 10, 0),
     (1, 11, 0),
     (1, 11, 0),
     (2, 0, 0),
     (2, 0, 0),
     (2, 1, 0),
     (2, 1, 0),
     (2, 2, 0),
     (2, 2, 0),
     (2, 3, 0),
     (2, 3, 0)]

In this example, we can see the age information of Eve's 20 recording sessions,
from 1 year and 6 months old to 2 years and 3 months old.

More on :ref:`headers`.

Transcript Data
---------------

Transcriptions as well as annotations from the ``%mor`` and ``%gra`` tiers
(for morphology, part-of-speech tags, and grammatical relations)
are accessible via NLTK-like
corpus access methods such as ``words()``, ``tagged_words()``, ``sents()``,
and ``tagged_sents()``.

By default, these methods each return a flat list of results from all the files.
If we are interested in the results for individual files,
these methods take the optional boolean parameter ``by_files``:

.. code-block:: python

    >>> words = eve.words()  # list of strings, for all the words across all 20 files
    >>> len(words)  # total word count
    119972
    >>> words[:8]
    ['more', 'cookie', '.', 'you', '0v', 'more', 'cookies', '?']
    >>> words_by_files = eve.words(by_files=True)  # list of lists of strings, each inner list for one file
    >>> len(words_by_files)  # expects 20 -- that's the number of files of ``eve``
    20
    >>> for words_one_file in words_by_files:
    ...     print(len(words_one_file))
    ...
    5840
    5309
    2493
    5753
    5709
    4350
    5314
    8901
    4462
    4535
    4196
    6214
    4464
    5202
    8075
    7361
    10872
    8407
    6903
    5612



``words()`` and other methods can optionally take the argument *participant*.
For instance, ``eve.words(participant='CHI')`` gets words by the target
child instead of all participants in the data.
(For more on the *participant* parameter, see :ref:`cds`.)

The "tagged" methods represent a word as a tuple of
(*word*, *pos*, *mor*, *rel*)
where *pos* is the part-of-speech tag, *mor* is the
morphological information (for the lemma and inflectional affix, for instance),
and *rel* is the dependency and grammatical relation:

.. code-block:: python

    >>> mother_tagged_words = eve.tagged_words(participant='MOT')
    >>> for tagged_word in mother_tagged_words[:20]:
    ...     print(tagged_word)
    ...
    ('you', 'PRO:PER', 'you', (1, 2, 'SUBJ'))
    ('0v', '0V', 'v', (2, 0, 'ROOT'))
    ('more', 'QN', 'more', (3, 4, 'QUANT'))
    ('cookies', 'N', 'cookie-PL', (4, 2, 'OBJ'))
    ('?', '?', '', (5, 2, 'PUNCT'))
    ('how_about', 'PRO:INT', 'how_about', (1, 3, 'LINK'))
    ('another', 'QN', 'another', (2, 3, 'QUANT'))
    ('grahamcracker', 'N', '+n|graham+n|cracker', (3, 0, 'INCROOT'))
    ('?', '?', '', (4, 3, 'PUNCT'))
    ('would', 'MOD', 'will&COND', (1, 3, 'AUX'))
    ('that', 'PRO:DEM', 'that', (2, 3, 'SUBJ'))
    ('do', 'V', 'do', (3, 0, 'ROOT'))
    ('just', 'ADV', 'just', (4, 5, 'JCT'))
    ('as_well', 'ADV', 'as_well', (5, 3, 'JCT'))
    ('?', '?', '', (6, 3, 'PUNCT'))
    ('here', 'ADV', 'here', (1, 0, 'INCROOT'))
    ('.', '.', '', (2, 1, 'PUNCT'))
    ('here', 'ADV', 'here', (1, 3, 'JCT'))
    ('you', 'PRO:PER', 'you', (2, 3, 'SUBJ'))
    ('go', 'V', 'go', (3, 0, 'ROOT'))

More on :ref:`transcriptions`.

.. _use_dev_measures:

Developmental measures
----------------------

To get the mean length of utterance (MLU) in morphemes, use ``MLUm()``:

.. code-block:: python

    >>> for filename, mlum in sorted(eve.MLUm().items()):
    ...     print(os.path.basename(filename), mlum)
    ...
    010600a.cha 2.267022696929239
    010600b.cha 2.4508196721311477
    010700a.cha 2.7628458498023716
    010700b.cha 2.571186440677966
    010800.cha 2.8528995756718527
    010900a.cha 3.1734317343173433
    010900b.cha 3.1268939393939394
    010900c.cha 3.380604796663191
    011000a.cha 3.8214971209213053
    011000b.cha 3.8062157221206583
    011100a.cha 3.87248322147651
    011100b.cha 4.157407407407407
    020000a.cha 4.247826086956522
    020000b.cha 3.9684873949579833
    020100a.cha 4.448895027624309
    020100b.cha 4.416536661466458
    020200a.cha 4.476769911504425
    020200b.cha 4.286978508217446
    020300a.cha 4.346094946401225
    020300b.cha 3.165120593692022

Other language developmental measures, such as type-token ratio (TTR) and
Index of Productive Syntax (IPSyn), are also implemented.
More on :ref:`devmeasures`


.. _use_word_freq:

Word frequency info, ngrams, search, and concordance
----------------------------------------------------

For word combinatorics, use ``word_frequency()`` and ``word_ngrams()``:

.. code-block:: python

    >>> word_freq = eve.word_frequency()
    >>> word_freq.most_common(5)
    [('.', 20130), ('?', 6358), ('you', 3695), ('the', 2524), ('it', 2365)]

    >>> bigrams = eve.word_ngrams(2)
    >>> bigrams.most_common(5)
    [(('it', '.'), 705), (('that', '?'), 619), (('what', '?'), 560), (('yeah', '.'), 510), (('there', '.'), 471)]

More on :ref:`freq`.

Questions? Issues?
------------------

If you have any questions, comments, bug reports etc, please open `issues
at the GitHub repository <https://github.com/jacksonllee/pylangacq/issues>`_, or
contact `Jackson L. Lee <https://jacksonllee.com/>`_.
