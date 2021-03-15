.. _frequencies:

Word Frequencies and Ngrams
===========================

Because word frequencies and combinatorics are useful for many purposes,
the following :class:`~pylangacq.chat.Reader` methods are defined:

.. currentmodule:: pylangacq.chat.Reader

.. autosummary::

    word_frequencies
    word_ngrams


For both :func:`~pylangacq.Reader.word_frequencies` and :func:`~pylangacq.Reader.word_ngrams`:

* They have the same optional arguments ``participants``, ``exclude``, and ``by_files``
  as :func:`~pylangacq.Reader.words`, :func:`~pylangacq.Reader.tokens`,
  :func:`~pylangacq.Reader.utterances` do.

* They have the optional argument ``keep_case``
  to specify whether upper/lowercase distinction should be kept or collapsed
  in counting words or ngrams.

* They return :class:`~collections.Counter` objects, which naturally represent
  a mapping from words or ngrams to their counts, and have useful methods
  for working with count data.


For illustration, let's check out some of the word trigrams in Eve's data from Brown.
To make it slightly more interesting,
we are going to look at child speech and child-directed speech separately.

.. code-block:: python

    >>> import pylangacq
    >>> url = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"
    >>> eve = pylangacq.read_chat(url, "Eve")
    >>>
    >>> trigrams_child_speech = eve.word_ngrams(3, participants="CHI")
    >>> trigrams_child_speech.most_common(10)  # A collections.Counter object has the method ``most_common``.
    [(('grape', 'juice', '.'), 74),
     (('another', 'one', '.'), 55),
     (('what', 'that', '?'), 50),
     (('a', 'b', 'c'), 47),
     (('right', 'there', '.'), 45),
     (('in', 'there', '.'), 43),
     (('b', 'c', '.'), 42),
     (('hi', 'Fraser', '.'), 39),
     (('I', 'want', 'some'), 39),
     (('a', 'minute', '.'), 35)]
    >>>
    >>> trigrams_child_directed_speech = eve.word_ngrams(3, exclude="CHI")
    >>> trigrams_child_directed_speech.most_common(10)
    [(("that's", 'right', '.'), 178),
     (('what', 'are', 'you'), 149),
     (('is', 'that', '?'), 124),
     (('do', 'you', 'want'), 104),
     (('what', 'is', 'that'), 99),
     (('are', 'you', 'doing'), 94),
     (("what's", 'that', '?'), 92),
     (('would', 'you', 'like'), 89),
     (('what', 'do', 'you'), 89),
     (('is', 'it', '?'), 89)]

Just this very brief result using word trigrams appears to show a contrast between
various demands being frequent in child speech,
versus the dominant usage of confirmation and attempts to get the child's
attention using questions in child-directed speech.
