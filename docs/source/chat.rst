.. _chat:

``chat`` --- Reading and parsing CHAT transcripts
=================================================

The ``chat`` module defines two classes
for reading and parsing CHAT transcripts:

.. currentmodule:: pylangacq.chat

.. autosummary::

   Reader
   SingleReader

The user does not usually need to call or create objects
directly with ``Reader`` or ``SingleReader`` in their code.
Under most circumstances, ``pylangchat.read_chat()`` is sufficient;
underlyingly, this function returns a ``Reader`` object
which relies on ``SingleReader`` for handling individual
data files.

Most of the methods of interest are those of the ``Reader`` class.
Many of them have the optional parameter ``by_files``.
By default, ``by_files`` is
``False`` and a given method X() returns whatever it is for all the files
in question. When ``by_files`` is set to be ``True``,
then the return object is dict(absolute-path filename: X() for that file)
instead.

The ``Reader`` methods are categorized into
:ref:`metadata_methods` and :ref:`data_methods`.

.. _metadata_methods:

Metadata methods
----------------

.. currentmodule:: pylangacq.chat.Reader

.. autosummary::

   filenames
   abspath
   number_of_files
   number_of_utterances
   headers
   participants
   participant_codes
   languages
   dates_of_recording
   age

.. _data_methods:

Data methods
------------

.. currentmodule:: pylangacq.chat.Reader

.. autosummary::

   index_to_tiers
   utterances
   words
   tagged_words
   sents
   tagged_sents
   part_of_speech_tags
   word_frequency
   word_ngrams
   search
   concordance
   MLU
   MLUm
   MLUw
   TTR
   IPSyn
   update
   add
   remove
   clear

.. _reader_api:

The ``Reader`` class API
------------------------

.. autoclass:: pylangacq.chat.Reader
   :members:
