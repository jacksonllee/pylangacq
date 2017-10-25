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

``'Brown/Eve/*.cha'`` matches all the 20 ``'.cha'`` files for Eve
(``'eve01.cha'``, ``'eve02.cha'``, etc):

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
    eve01.cha 5843
    eve02.cha 5310
    eve03.cha 2494
    eve04.cha 5757
    eve05.cha 5715
    eve06.cha 4353
    eve07.cha 5320
    eve08.cha 8902
    eve09.cha 4466
    eve10.cha 4535
    eve11.cha 4200
    eve12.cha 6218
    eve13.cha 4469
    eve14.cha 5203
    eve15.cha 8099
    eve16.cha 7385
    eve17.cha 10885
    eve18.cha 8425
    eve19.cha 6929
    eve20.cha 5625

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
    ('you', 'PRO', 'you', (1, 2, 'SUBJ'))
    ('0v', '0V', 'v', (2, 0, 'ROOT'))
    ('more', 'QN', 'more', (3, 4, 'QUANT'))
    ('cookies', 'N', 'cookie-PL', (4, 2, 'OBJ'))
    ('?', '?', '', (5, 2, 'PUNCT'))
    ('how_about', 'ADV:WH', 'how_about', (1, 3, 'LINK'))
    ('another', 'QN', 'another', (2, 3, 'QUANT'))
    ('graham+cracker', 'N', '+n|graham+n|cracker', (3, 0, 'INCROOT'))
    ('?', '?', '', (4, 3, 'PUNCT'))
    ('would', 'MOD', 'will&COND', (1, 3, 'AUX'))
    ('that', 'DET', 'that', (2, 3, 'DET'))
    ('do', 'V', 'do', (3, 0, 'ROOT'))
    ('just', 'ADV', 'just', (4, 3, 'JCT'))
    ('as_well', 'ADV', 'as_well', (5, 3, 'JCT'))
    ('?', '?', '', (6, 3, 'PUNCT'))
    ('here', 'ADV', 'here', (1, 0, 'INCROOT'))
    ('.', '.', '', (2, 1, 'PUNCT'))
    ('here', 'ADV', 'here', (1, 3, 'JCT'))
    ('you', 'PRO', 'you', (2, 3, 'SUBJ'))
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
    eve01.cha 2.267022696929239
    eve02.cha 2.4487704918032787
    eve03.cha 2.7628458498023716
    eve04.cha 2.5762711864406778
    eve05.cha 2.8585572842998586
    eve06.cha 3.177121771217712
    eve07.cha 3.1231060606060606
    eve08.cha 3.3743482794577684
    eve09.cha 3.817658349328215
    eve10.cha 3.7915904936014626
    eve11.cha 3.865771812080537
    eve12.cha 4.157407407407407
    eve13.cha 4.239130434782608
    eve14.cha 3.9600840336134455
    eve15.cha 4.4502762430939224
    eve16.cha 4.4243369734789395
    eve17.cha 4.46570796460177
    eve18.cha 4.288242730720607
    eve19.cha 4.347626339969372
    eve20.cha 3.163265306122449

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
    [('.', 20130), ('?', 6359), ('you', 3695), ('the', 2524), ('it', 2363)]

    >>> bigrams = eve.word_ngrams(2)
    >>> bigrams.most_common(5)
    [(('it', '.'), 703), (('that', '?'), 618), (('what', '?'), 560), (('yeah', '.'), 510), (('there', '.'), 471)]

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

