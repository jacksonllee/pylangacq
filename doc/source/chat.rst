.. _chat:

``chat`` --- Reading and parsing CHAT transcripts
=================================================

The ``chat`` module defines classes for reading and parsing CHAT transcripts.

.. currentmodule:: pylangacq.chat

.. autosummary::

   Reader
   SingleReader

A good number of methods share the same name across both ``Reader`` and
``SingleReader`` classes. The methods in question in ``Reader``
return a dict that maps
an absolute-path filename to the file's returned object from the corresponding
method in ``SingleReader``.
For example, ``date()`` in ``SingleReader`` returns the date of the file in
question, whereas ``date()`` in ``Reader`` returns a dict mapping filenames to
individual files' ``date()``.

These "shared" methods are as follows:

.. currentmodule:: pylangacq.chat.SingleReader

.. autosummary::

   age
   date
   headers
   index_to_tiers
   languages
   number_of_utterances
   participant_codes
   participants
   sents
   tagged_sents
   tagged_words
   utterances
   word_frequency
   words

Methods specific to the ``Reader`` class:

.. currentmodule:: pylangacq.chat.Reader

.. autosummary::

   all_sents
   all_tagged_sents
   all_tagged_words
   all_words
   filenames
   number_of_files
   total_number_of_utterances

Methods specific to the ``SingleReader`` class:

.. currentmodule:: pylangacq.chat.SingleReader

.. autosummary::

   cha_lines
   filename

The full details of the ``chat`` module are documented below.

--------------------------------

.. automodule:: pylangacq.chat
   :members:
