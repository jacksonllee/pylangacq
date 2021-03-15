.. _frequencies:

Word Frequencies and Ngrams
===========================

.. currentmodule:: pylangacq.Reader

.. autosummary::

    word_frequencies
    word_ngrams


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
    >>> word_freq_CDS = eve.word_frequency(exclude='CHI')  # child-directed speech
    >>> word_freq_child = eve.word_frequency(participant='CHI')  # child speech
    >>> word_freq.most_common(5)
    [('.', 20130), ('?', 6358), ('you', 3695), ('the', 2524), ('it', 2365)]
    >>> word_freq_CDS.most_common(5)
    [('.', 9687), ('?', 4909), ('you', 3061), ('the', 1966), ('it', 1563)]
    >>> word_freq_child.most_common(5)
    [('.', 10443), ('?', 1449), ('I', 1199), ('that', 1051), ('a', 968)]

This tiny example already shows a key and expected difference ("you" versus "I")
between child speech and
child directed speech in terms of pronoun distribution.

For ``word_ngrams(n)``:

.. code-block:: python

    >>> from pprint import pprint
    >>> trigrams_CDS = eve.word_ngrams(3, exclude='CHI')  # 3 for trigrams; for child-directed speech
    >>> trigrams_child = eve.word_ngrams(3, participant='CHI')  # child speech
    >>> pprint(trigrams_CDS.most_common(5))  # lots of questions in child-directed speech!
    [(("that's", 'right', '.'), 178),
     (('what', 'are', 'you'), 149),
     (('is', 'that', '?'), 124),
     (('do', 'you', 'want'), 104),
     (('what', 'is', 'that'), 99)]
    >>> pprint(trigrams_child.most_common(5))
    [(('grape', 'juice', '.'), 74),
     (('another', 'one', '.'), 55),
     (('what', 'that', '?'), 50),
     (('a', 'b', 'c'), 47),
     (('right', 'there', '.'), 45)]
