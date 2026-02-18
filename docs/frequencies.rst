.. _frequencies:

Word Frequencies and Ngrams
===========================

For word combinatorics, :class:`~pylangacq.CHAT` provides the
:meth:`~pylangacq.CHAT.word_ngrams` method:

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    word_ngrams

:meth:`~pylangacq.CHAT.word_ngrams` takes a single required argument ``n``
for the n-gram order.
It returns an :class:`pylangacq.Ngrams` object, which stores ngrams efficiently and
provides useful methods such as :meth:`~pylangacq.Ngrams.most_common`, :meth:`~pylangacq.Ngrams.to_counter`,
:meth:`~pylangacq.Ngrams.items`, and :meth:`~pylangacq.Ngrams.count`.

N-grams do not cross utterance boundaries.

To filter by participant, use :meth:`~pylangacq.CHAT.filter`
before calling :meth:`~pylangacq.CHAT.word_ngrams`.

For illustration, let's check out some of the word trigrams in Eve's data from Brown.
To make it slightly more interesting,
we are going to look at child speech and child-directed speech separately.

.. code-block:: python

    import pylangacq
    brown = pylangacq.read_chat("path/to/your/local/Brown.zip")
    eve = brown.filter(files="Eve")
    eve_chi = eve.filter(participants="CHI")
    eve_cds = eve.filter(participants="^(?!CHI$)")

    trigrams_child_speech = eve_chi.word_ngrams(3)
    trigrams_child_speech.most_common(10)
    # [(('grape', 'juice', '.'), 74),
    #  (('what', 'that', '?'), 50),
    #  (('a@l', 'b@l', 'c@l'), 47),
    #  (('right', 'there', '.'), 45),
    #  (('another', 'one', '.'), 45),
    #  (('in', 'there', '.'), 43),
    #  (('b@l', 'c@l', '.'), 42),
    #  (('hi', 'Fraser', '.'), 39),
    #  (('I', 'want', 'some'), 39),
    #  (('a', 'minute', '.'), 35)]

    trigrams_child_directed_speech = eve_cds.word_ngrams(3)
    trigrams_child_directed_speech.most_common(10)
    # [(("that's", 'right', '.'), 178),
    #  (('what', 'are', 'you'), 149),
    #  (('is', 'that', '?'), 124),
    #  (('what', 'is', 'that'), 99),
    #  ((',', 'Eve', '.'), 95),
    #  (('are', 'you', 'doing'), 94),
    #  (("what's", 'that', '?'), 92),
    #  (('would', 'you', 'like'), 89),
    #  (('is', 'it', '?'), 89),
    #  (('what', 'did', 'you'), 77)]

Just this very brief result using word trigrams appears to show a contrast between
various demands being frequent in child speech,
versus the dominant usage of confirmation and attempts to get the child's
attention using questions in child-directed speech.

The :meth:`~pylangacq.CHAT.word_ngrams` method returns an :class:`pylangacq.Ngrams` object,
which has the :meth:`~pylangacq.Ngrams.most_common` method as used above.
If you need a :class:`~collections.Counter` instead,
call :meth:`~pylangacq.Ngrams.to_counter` on the :class:`pylangacq.Ngrams` object:

.. code-block:: python

    counter = trigrams_child_speech.to_counter()
    type(counter)
    # <class 'collections.Counter'>
    counter.most_common(5)
    # [(('grape', 'juice', '.'), 74),
    #  (('what', 'that', '?'), 50),
    #  (('a@l', 'b@l', 'c@l'), 47),
    #  (('right', 'there', '.'), 45),
    #  (('another', 'one', '.'), 45)]

For word frequencies, use ``word_ngrams(1)`` to get unigrams:

.. code-block:: python

    word_freq_chi = eve_chi.word_ngrams(1)
    word_freq_chi.most_common(5)
    # [(('.',), 10389),
    #  (('?',), 1449),
    #  (('I',), 1197),
    #  (('that',), 1047),
    #  (('a',), 883)]

Note that unigrams are represented as single-element tuples,
consistent with how all ngrams are tuples regardless of n.
