.. _quickstart:

Quickstart
==========

This page introduces the basic functionalities of PyLangAcq and points to
relevant pages of the library documentation for more advanced usage.

* :ref:`test_install`
* :ref:`read_data`
* :ref:`get_metadata`
* :ref:`transcripts`
* :ref:`use_dev_measures`
* :ref:`use_word_freq`

.. _test_install:

Testing the library installation
--------------------------------

To test that PyLangAcq is installed on your system (see :ref:`download`), open your terminal with
your Python interpretor of choice (= the one for installing PyLangAcq):

.. code-block:: python

    >>> import pylangacq

If all goes well, there should be no import errors.

.. _read_data:

Reading CHAT data
-----------------

Assuming that the CHAT transcripts for the Brown portion of CHILDES
(`zipped here <https://childes.talkbank.org/data/Eng-NA/Brown.zip>`_)
are available at the current directory,
we can read the Eve data using PyLangAcq:

.. code-block:: python

    >>> import pylangacq as pla
    >>> eve = pla.read_chat('Brown/Eve/*.cha')

``'Brown/Eve/*.cha'`` matches all the 20 ``'.cha'`` files for Eve:

.. code-block:: python

    >>> eve.number_of_files()
    20

More on :ref:`read`.

.. _get_metadata:

Metadata
--------

CHAT transcripts store metadata as headers with lines beginning with
``@``. For instance, we can retrieve the age information of the target child
in ``eve`` created above:

.. code-block:: python

    >>> from pprint import pprint
    >>> pprint(sorted(eve.age().values()))
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

``eve.age()`` returns a dict that maps a filename to the respective
file's age information (as a 3-tuple, e.g., ``(1, 6, 0)`` for 1 year and
6 months).

More on :ref:`metadata`.

.. _transcripts:

Transcriptions and annotations
------------------------------


Transcriptions and annotations from the ``%mor`` and ``%gra`` tiers
(for morphology, part-of-speech tags, and grammatical relations)
are accessible via NLTK-like
corpus access methods such as ``words()``, ``tagged_words()``, ``sents()``,
and ``tagged_sents()``. By default, these methods
return an object "X" lumping together results from all the files.
If we are interested in return objects for individual files and therefore need
the file structure, these methods take the optional parameter ``by_files``: if
``True``, the return object is "dict(filename: X for that file)"
a dict mapping an absolute-path filename to the method's return
object for that file (similar to ``age()`` introduced above). For example,
to check out the word counts in ``eve``:

.. code-block:: python

    >>> filenames = eve.filenames()  # the set of 20 absolute-path filenames
    >>> words = eve.words()  # all words across as a list across all 20 files
    >>> len(words)  # total word count
    119972
    >>> words[:8]
    ['more', 'cookie', '.', 'you', '0v', 'more', 'cookies', '?']
    >>> words_by_files = eve.words(by_files=True)  # dict(filename: word list for that file)
    >>> import os
    >>> for filename in sorted(filenames):
    ...     print(os.path.basename(filename), len(words_by_files[filename]))
    ...
    010600a.cha 5840
    010600b.cha 5309
    010700a.cha 2493
    010700b.cha 5753
    010800.cha 5709
    010900a.cha 4350
    010900b.cha 5314
    010900c.cha 8901
    011000a.cha 4462
    011000b.cha 4535
    011100a.cha 4196
    011100b.cha 6214
    020000a.cha 4464
    020000b.cha 5202
    020100a.cha 8075
    020100b.cha 7361
    020200a.cha 10872
    020200b.cha 8407
    020300a.cha 6903
    020300b.cha 5612

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
