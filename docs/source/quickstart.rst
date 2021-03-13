.. _quickstart:

Quickstart
==========

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
To illustrate, let's use Eve's data from the
`Brown <https://childes.talkbank.org/access/Eng-NA/Brown.html>`_
corpus of American English:

.. code-block:: python

    >>> url = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"
    >>> eve = pylangacq.read_chat(url, "Eve")
    >>> len(eve)
    20

``eve`` is a :class:`~pycantonese.Reader` instance.
It has Eve's 20 CHAT data files all parsed and ready for your analysis.
``eve`` has various methods through which you can access different information
with Pythonic data structures.

More on :ref:`read`.

Header Information
------------------

CHAT transcript files store metadata in the header with lines beginning with ``@``.
Among other things, ``eve`` has the age information of Eve when the recordings were made,
which is from 1 year and 6 months old to 2 years and 3 months old:

.. code-block:: python

    >>> eve.ages()
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

More on :ref:`headers`.

Transcriptions and Annotations
------------------------------

``words()`` is the basic method to access the transcriptions:

.. code-block:: python

    >>> words = eve.words()  # list of strings, for all the words across all 20 files
    >>> len(words)  # total word count
    119972
    >>> words[:8]
    ['more', 'cookie', '.', 'you', '0v', 'more', 'cookies', '?']

By default, ``words()`` returns a flat list of results from all the files.
If we are interested in the results for individual files,
the method has the optional boolean parameter ``by_files``:

.. code-block:: python

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

Apart from transcriptions, CHAT data has rich annotations for linguistic
and extra-linguistic information.
Such annotations are accessible through the methods ``tokens()`` and ``utterances()``.

Many CHAT datasets on CHILDES have the ``%mor`` and ``%gra`` tiers
for morphological information and grammatical relations, respectively.
A reader such as ``eve`` from above has all this information readily available
to you via the ``tokens()`` method -- think of ``tokens()`` as ``words()`` with annotations:

.. code-block:: python

    >>> some_tokens = eve.tokens()[:5]
    >>> some_tokens
    [Token(word='more', pos='qn', mor='more', gra=Gra(source=1, target=2, rel='QUANT')),
     Token(word='cookie', pos='n', mor='cookie', gra=Gra(source=2, target=0, rel='INCROOT')),
     Token(word='.', pos='.', mor='', gra=Gra(source=3, target=2, rel='PUNCT')),
     Token(word='you', pos='pro:per', mor='you', gra=Gra(source=1, target=2, rel='SUBJ')),
     Token(word='0v', pos='0v', mor='v', gra=Gra(source=2, target=0, rel='ROOT'))]
    >>>
    >>> # The Token class is a dataclass. A Token instance has attributes as shown above.
    >>> for token in some_tokens:
    ...     print(token.word, token.pos)
    ...
    more qn
    cookie n
    . .
    you pro:per
    0v 0v

Beyond the ``%mor`` and ``%gra`` tiers,
an utterance has yet more information from the original CHAT data file.
If you need information such as the unsegmented transcription, time marks,
or any unparsed tiers, the method ``utterances()`` is what you need:

.. code-block:: python

    >>> eve.utterances()[0]
    Utterance(participant='CHI',
              tokens=[Token(word='more', pos='qn', mor='more', gra=Gra(source=1, target=2, rel='QUANT')),
                      Token(word='cookie', pos='n', mor='cookie', gra=Gra(source=2, target=0, rel='INCROOT')),
                      Token(word='.', pos='.', mor='', gra=Gra(source=3, target=2, rel='PUNCT'))],
              time_marks=None,
              tiers={'CHI': 'more cookie . [+ IMP]',
                     '%mor': 'qn|more n|cookie .',
                     '%gra': '1|2|QUANT 2|0|INCROOT 3|2|PUNCT',
                     '%int': 'distinctive , loud'})

More on :ref:`transcriptions`.

Developmental Measures
----------------------

To get the mean length of utterance (MLU), use the method ``mlu()``:

.. code-block:: python

    >>> eve.mlu()
    [2.316421895861148,
     2.5163934426229506,
     2.8063241106719365,
     2.611864406779661,
     2.8854314002828856,
     3.195571955719557,
     3.1818181818181817,
     3.4171011470281543,
     3.840690978886756,
     3.822669104204753,
     3.883668903803132,
     4.165123456790123,
     4.269565217391304,
     3.976890756302521,
     4.457182320441989,
     4.422776911076443,
     4.495575221238938,
     4.292035398230088,
     4.3813169984686064,
     3.320964749536178]

The result is the MLU for each CHAT file.
As this is a list of floats, they can be readily piped into
other packages for making plots, for example.

The other language developmental measures implemented so far are
``ttr()`` for the type-token ratio (TTR) and
``ipsyn()`` for the index of productive syntax (IPSyn).

More on :ref:`measures`.

Word Frequencies and Ngrams
---------------------------

For word combinatorics, check out ``word_frequencies()`` and ``word_ngrams()``:

.. code-block:: python

    >>> word_freq = eve.word_frequencies()  # a collections.Counter object
    >>> word_freq.most_common(5)
    [('.', 20130),
     ('?', 6358),
     ('you', 3695),
     ('the', 2524),
     ('it', 2365)]

    >>> bigrams = eve.word_ngrams(2)  # a collections.Counter object
    >>> bigrams.most_common(5)
    [(('it', '.'), 705),
     (('that', '?'), 619),
     (('what', '?'), 560),
     (('yeah', '.'), 510),
     (('there', '.'), 471)]

More on :ref:`frequencies`.

Questions? Issues?
------------------

If you have any questions, comments, bug reports etc, please open `issues
at the GitHub repository <https://github.com/jacksonllee/pylangacq/issues>`_, or
contact `Jackson L. Lee <https://jacksonllee.com/>`_.
