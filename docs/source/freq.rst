.. _freq:

Word frequency and ngrams
=========================

The way words combine in natural language data is of great interest in all areas
of linguistic research.
PyLangAcq provides several handy functionality for word combinatorics.

We are often interested in word frequency information and word ngrams:

====================  =================================================
Method                Return object
====================  =================================================
``word_frequency()``  Counter dict(word: word token count)
``word_ngrams(n)``    Counter dict(ngram as a tuple: ngram token count)
====================  =================================================

Both methods return
`Counter dicts from collections <https://docs.python.org/3/library/collections.html#collections.Counter>`_
in the Python standard
library. As a result (and as an advantage!), all Counter methods apply to
the return objects of these methods.

``word_frequency()`` and ``word_ngrams(n)`` (with the obligatory parameter
*n*) share the following optional parameters:

* ``participant``: see :ref:`cds`
* ``by_files``: see :ref:`reader_properties`
* ``keep_case``: whether case distinction such as "Rocky" and "rocky" is kept;
  defaults to ``True``. If "Rocky" and "rocky" are treated as distinct, then
  they are two distinct word types and have separate key:value entries in the
  return object.

To illustrate, we set up a ``Reader`` instance ``eve``
based on Eve's data from CHILDES Brown:

.. code-block:: python

    >>> import pylangacq as pla
    >>> eve = pla.read_chat('Brown/Eve/*.cha')

We use the ``participant`` parameter and the
``most_common()`` method available for Counter dicts below.

For ``word_frequency()``:

.. code-block:: python

    >>> word_freq = eve.word_frequency()  # all participants
    >>> word_freq_CDS = eve.word_frequency(participant='^(?!.*CHI).*$')  # child-directed speech
    >>> word_freq_child = eve.word_frequency(participant='CHI')  # only the target child
    >>> word_freq.most_common(5)
    [('.', 20130), ('?', 6359), ('you', 3695), ('the', 2524), ('it', 2363)]
    >>> word_freq_CDS.most_common(5)
    [('.', 9687), ('?', 4910), ('you', 3061), ('the', 1966), ('it', 1563)]
    >>> word_freq_child.most_common(5)
    [('.', 10443), ('?', 1449), ('I', 1198), ('that', 1050), ('a', 883)]

This tiny example already shows a key and expected difference ("you" versus "I")
between child speech and
child directed speech in terms of pronoun distribution.

For ``word_ngrams(n)``:

.. code-block:: python

    >>> bigrams = eve.word_ngrams(2)  # all participants
    >>> bigrams_CDS = eve.word_ngrams(2, participant='^(?!.*CHI).*$')  # exclude the target child
    >>> bigrams_child = eve.word_ngrams(2, participant='CHI')  # only the target child
    >>> bigrams.most_common(5)
    [(('it', '.'), 703), (('that', '?'), 618), (('what', '?'), 560), (('yeah', '.'), 510), (('there', '.'), 471)]
    >>> bigrams_CDS.most_common(5)
    [(('what', '?'), 503), (('it', '.'), 346), (('on', 'the'), 327), (('are', 'you'), 308), (('in', 'the'), 301)]
    >>> bigrams_child.most_common(5)
    [(('it', '.'), 357), (('that', '?'), 326), (('yeah', '.'), 326), (('no', '.'), 296), (('there', '.'), 253)]

