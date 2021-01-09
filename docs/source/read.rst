.. _read:

Reading data
============

This page provides details of the CHAT data format that PyLangAcq assumes and
explains how CHAT data files are read.

* :ref:`chat_format`
* :ref:`initialize_reader`
* :ref:`reader_properties`
* :ref:`add_remove_transcripts`


.. _chat_format:

The CHAT transcription format
-----------------------------

PyLangAcq is designed to handle the CHAT transcription format as used in the
CHILDES database for language acquisition research.
The bare minimum of what PyLangAcq assumes about CHAT is explained here.
(As of January 2016, PyLangAcq conforms to the latest
`CHAT manual <https://talkbank.org/manuals/CHAT.pdf>`_
dated September 22, 2015.)

**Headers**

A CHAT transcript file (typically with the extension name ``.cha``, though not
strictly required) provides metadata headers using lines starting with ``@``.
Among the many possible headers,
``@Participants`` and ``@ID`` are of particular interest::

    @Participants: Code1 Name1 Role1 , Code2 Name2 Role2
    @ID: ||Code1|1;6.||||Role1|||
    @ID: ||Code2|||||Role2|||

The ``@Participants`` header states the participants of the transcript. In this
hypothetical example shown just above, there are two participants.
Each participant has a participant code (e.g., ``Code1``), a participant name
(e.g., ``Name1``), and a participant role (e.g., ``Role1``).
The participant code must be an alphanumeric three-character string
which begins with a letter, and all letters must be in uppercase.
The participant code must come first, immediately
followed by a space, and then by the participant name, and in turn by
another space and then the participant role. A comma separates
information between two participants.

If there are ``@ID`` headers, they must appear after, but not before, the
``@Participants`` header.
The number of ``@ID`` headers is equal to the number of participants.
An ``@ID`` header contains detailed information about a
participant::

    language|corpus|participant_code|age|sex|group|SES|participant_role|education|custom|

Within ``@ID``, the fields ``participant_code`` and ``participant_role``
must match the information of the relevant participant in the ``@Participants``
header.
Often of interest in language acquisition research is the age of the
participant (e.g., the target child). For instance, the age of
participant ``Code1`` is 1 year and 6 months, as given by ``1;6.``.
Fields are left empty if no information is available.

While all other ``@`` headers are optional, PyLangAcq has built-in functions
specifically for ``@Languages`` and ``@Date`` for potential usage.


**Transcriptions**

After the headers come the transcriptions. All transcriptions are signaled by
``*`` at the beginning of the line::

    *Code1: good morning .

``*`` is immediately followed by the participant code (e.g., ``Code1``), and then
by a colon ``:`` and a space (or tab). Then the transcribed line follows.

For research purposes, many CHAT transcripts have additional tiers signaled by
``%mor`` (for morphological information such as part-of-speech tag and lemma),
``%gra`` (for dependency and grammatical relations), and other ``%`` tiers.
Much of what PyLangAcq can do relies on the annotations in these tiers with
rich linguistic information.


**Line continuations**

For any header and transcription lines that are too long, line continuations
are allowed in CHAT files with a tab character (denoted by ``<TAB>`` below), from::

    *Code1: this line is to demonstrate how line continuations are done in CHAT .

to::

    *Code1: this line is to demonstrate how line continuations
    <TAB>are done in CHAT .

This implies that all lines in a CHAT file must begin with any of the following
characters only: ``@``, ``*``, ``%``, ``<TAB>``.


.. _initialize_reader:

Initializing a Reader instance
------------------------------

Assuming that the CHAT transcripts for the Brown portion of CHILDES
(i.e., ``eve01.cha``, ``eve02.cha`` etc.)
are at the current directory:

.. code-block:: python

    >>> import pylangacq as pla
    >>> eve = pla.read_chat('Brown/Eve/*.cha')

.. NOTE::
   The UTF-8 encoding is assumed for all CHAT files.
   If your data files are encoded differently (e.g., in Latin-1 instead),
   ``read_chat`` takes the keyword argument ``'encoding'``. For instance,
   you can read in data like this::

      data = pla.read_chat('path/to/data/files', encoding='latin1')

``read_chat()`` can take one or multiple filenames.
These filenames can be either relative paths to the current directory
(as exemplified here) or
absolute paths. Filename pattern matching with ``*``
(wildcard for zero or more characters) and ``?`` (wildcard for one or more
characters) can be used. In this example with Eve's files, ``*`` matches all
the 20 CHAT
files in the subdirectory ``Brown/Eve/`` relative to the current directory.

``read_chat()`` returns an instance of the
``pylangacq.chat.Reader``
class. For example, ``eve`` is a ``pylangacq.chat.Reader`` instance,
or simply ``Reader`` instance for short.
Most of the functionality of PyLangAcq is accessed via methods of ``Reader``
instances, in the form of ``reader_instance.method_name()``.


If your CHAT data comes as an in-memory string (a string of what a single
CHAT data file would look like), a ``Reader`` instance can be created by
the ``from_chat_str`` class method:

.. code-block:: python

    >>> import pylangacq as pla
    >>> reader = pla.Reader.from_chat_str(your_chat_data_str, encoding='utf-8')


.. _reader_properties:

Reader methods
--------------

Basic information of a ``Reader`` instance such as ``eve`` can be accessed
as follows:

.. code-block:: python

    >>> eve.number_of_files()  # from eve01.cha through eve20.cha
    20
    >>> len(eve)  # same as number_of_files()
    20
    >>> eve.number_of_utterances()  # across all 20 files and all participants
    26979

The bulk of the library documentation is about the various ``Reader`` methods.
The full API details can be found in :ref:`reader_api`.

For the method ``number_of_utterances()``, an utterance is a transcription line that
begins with ``*`` in the CHAT transcripts.


Many methods of ``Reader`` have a dual structure in terms of the return object.
It depends on whether or not you are interested in an return object that
organizes contents by the individual source files.
These methods have the optional parameter ``by_files`` (default: ``False``).
For a given method ``some_method()`` called for a ``Reader`` instance named ``reader_instance``:

==============================================  =============================================================
Method                                          Return object
==============================================  =============================================================
``reader_instance.some_method()``               whatever ``some_method()`` is for all files in ``reader_instance``, with no knowledge of the file structure
``reader_instance.some_method(by_files=True)``  dict(absolute-path filename: ``some_method()`` for that file)
==============================================  =============================================================

``number_of_utterances()`` is one of the methods with ``by_files``:

.. code-block:: python

    >>> eve.number_of_utterances()  # by_files is False by default
    26979
    >>> counts_by_files = eve.number_of_utterances(by_files=True)  # dict(filename: num of utterances)
    >>> import os
    >>> for abs_filename, n in sorted(counts_by_files.items()):
    ...     print(os.path.basename(abs_filename), n)
    ...
    010600a.cha 1601
    010600b.cha 1304
    010700a.cha 618
    010700b.cha 1456
    010800.cha 1479
    010900a.cha 1075
    010900b.cha 1277
    010900c.cha 2058
    011000a.cha 1024
    011000b.cha 1060
    011100a.cha 952
    011100b.cha 1339
    020000a.cha 959
    020000b.cha 1094
    020100a.cha 1651
    020100b.cha 1500
    020200a.cha 2156
    020200b.cha 1760
    020300a.cha 1348
    020300b.cha 1268

(Many data access methods have the parameter ``by_files``
for the dual possibilities of return objects;
see :ref:`transcriptions`.)

We are often interested in what concerns specific participants in the data,
e.g., the target child whose participant code is ``'CHI'``.
Many
methods accept an optional argument to specify the parameter ``participant``
(see also :ref:`cds`):

.. code-block:: python

    >>> for abs_filename, n in sorted(eve.number_of_utterances(participant='CHI', by_files=True).items()):
    ...     print(os.path.basename(abs_filename), n)
    ...
    010600a.cha 749
    010600b.cha 488
    010700a.cha 253
    010700b.cha 590
    010800.cha 707
    010900a.cha 542
    010900b.cha 528
    010900c.cha 959
    011000a.cha 521
    011000b.cha 547
    011100a.cha 447
    011100b.cha 648
    020000a.cha 460
    020000b.cha 476
    020100a.cha 724
    020100b.cha 641
    020200a.cha 904
    020200b.cha 791
    020300a.cha 653
    020300b.cha 539


.. _add_remove_transcripts:

Adding and removing transcripts in a reader
-------------------------------------------

It is possible to add or remove transcripts in a ``Reader`` instance;
this is important where dynamic data handling is needed.
Three methods are available:
``add()``, ``remove()``, ``update()``, and ``clear()``.

To illustrate, we initialize ``corpus`` as an empty ``Reader`` instance:

.. code-block:: python

    >>> corpus = pla.read_chat()  # empty, no filenames given

To add transcripts, use ``add()`` which takes one or more filenames
as arguments:

.. code-block:: python

    >>> corpus.add('Brown/Eve/01*.cha')  # all data prior to 2;0. (files are conveniently named by age)
    >>> corpus.number_of_files()
    12

To remove transcripts with ``remove()``:

.. code-block:: python

    >>> corpus.remove('Brown/Eve/010*.cha')  # remove data files prior to 1;10.
    >>> corpus.number_of_files()
    4

``update()`` takes a ``Reader`` instance and updates the current one:

.. code-block:: python

    >>> new_corpus = pla.read_chat('Brown/Eve/02*.cha')  # all data from 2;0.
    >>> new_corpus.number_of_files()
    8
    >>> corpus.update(new_corpus)  # use "update" to combine new_corpus into corpus
    >>> corpus.number_of_files()
    12

``clear()`` applies to a ``Reader`` instance to clear everything and reset it
as an empty ``Reader`` instance:

.. code-block:: python

    >>> corpus.clear()
    >>> corpus.number_of_files()
    0
