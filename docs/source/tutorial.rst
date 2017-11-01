.. _tutorial:

Tutorial
========

This page introduces the basic functionalities of PyLangAcq and points to
relevant pages of the library documentation for more advanced usage.

* :ref:`test_install`
* :ref:`read_data`
* :ref:`get_metadata`
* :ref:`transcripts`
* :ref:`use_dev_measures`
* :ref:`use_word_freq`
* :ref:`by_lx_areas`


.. NOTE::
   Python 3 syntax is used throughout this tutorial and other pages.
   If you are using Python 2, the "print" statements such as::

       print('something', 'something else')

   should be converted to the following::

       print 'something', 'something else'


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
    120133
    >>> words[:10]
    ['more', 'cookie', '.', 'you', '0v', 'more', 'cookies', '?']
    >>> words_by_files = eve.words(by_files=True)  # dict(filename: word list for that file)
    >>> import os
    >>> for filename in sorted(filenames):
    ...     print(os.path.basename(filename), len(words_by_files[filename]))
    ...
    010600a.cha 5843
    010600b.cha 5310
    010700a.cha 2492
    010700b.cha 5757
    010800.cha 5715
    010900a.cha 4353
    010900b.cha 5320
    010900c.cha 8902
    011000a.cha 4466
    011000b.cha 4535
    011100a.cha 4200
    011100b.cha 6218
    020000a.cha 4469
    020000b.cha 5203
    020100a.cha 8099
    020100b.cha 7385
    020200a.cha 10885
    020200b.cha 8425
    020300a.cha 6929
    020300b.cha 5625

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
    ('how_about', 'ADV:INT', 'how_about', (1, 3, 'LINK'))
    ('another', 'QN', 'another', (2, 3, 'QUANT'))
    ('grahamcracker', 'N', '+n|graham+n|cracker', (3, 0, 'INCROOT'))
    ('?', '?', '', (4, 3, 'PUNCT'))
    ('would', 'MOD', 'will&COND', (1, 3, 'AUX'))
    ('that', 'PRO:REL', 'that', (2, 3, 'LINK'))
    ('do', 'V', 'do', (3, 0, 'ROOT'))
    ('just', 'ADV', 'just', (4, 3, 'JCT'))
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
    010600a.cha 2.265687583444593
    010600b.cha 2.4487704918032787
    010700a.cha 2.7628458498023716
    010700b.cha 2.5728813559322035
    010800.cha 2.8528995756718527
    010900a.cha 3.1660516605166054
    010900b.cha 3.115530303030303
    010900c.cha 3.3733055265901983
    011000a.cha 3.817658349328215
    011000b.cha 3.7915904936014626
    011100a.cha 3.859060402684564
    011100b.cha 4.154320987654321
    020000a.cha 4.239130434782608
    020000b.cha 3.96218487394958
    020100a.cha 4.44475138121547
    020100b.cha 4.405616224648986
    020200a.cha 4.462389380530974
    020200b.cha 4.2768647281921615
    020300a.cha 4.339969372128637
    020300b.cha 3.1521335807050095

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

See also ``search()`` and ``concordance()`` in :ref:`concord`.

.. _by_lx_areas:

Acquisition by linguistic areas
-------------------------------


* :ref:`lex`
* :ref:`phono`
* :ref:`synsem`
* :ref:`disca`


Questions? Issues?
------------------

If you have any questions, comments, bug reports etc, please open `issues
at the GitHub repository <https://github.com/pylangacq/pylangacq/issues>`_, or
contact `Jackson L. Lee <http://jacksonllee.com/>`_.

