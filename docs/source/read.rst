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
`CHAT manual <http://childes.psy.cmu.edu/manuals/CHAT.pdf>`_
dated September 22, 2015.)

**Headers**

A CHAT transcript file (typically with the extension name ``.cha``, though not
strictly required) provides metadata headers using lines starting with ``@``.
Among the many possible headers,
``@Participants`` and ``@ID`` are of particular interest::

    @Participants: XX1 Name1 Role1 , XX2 Name2 Role2
    @ID: ||XX1|1;6.||||Role1|||
    @ID: ||XX2|||||Role2|||

The ``@Participants`` header states the participants of the transcript. In this
hypothetical example shown just above, there are two participants.
Each participant has a participant code (e.g., ``XX1``), a participant name
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
participant ``XX1`` is 1 year and 6 months, as given by ``1;6.``.
Fields are left empty if no information is available.

While all other ``@`` headers are optional, PyLangAcq has built-in functions
specifically for ``@Languages`` and ``@Date`` for potential usage.


**Transcriptions**

After the headers come the transcriptions. All transcriptions are signaled by
``*`` at the beginning of the line::

    *XX1: good morning .

``*`` is immediately followed by the participant code (e.g., ``XX1``), and then
by a colon ``:`` and a space (or tab). Then the transcribed line follows.

For research purposes, many CHAT transcripts have additional tiers signaled by
``%mor`` (for morphological information such as part-of-speech tag and lemma),
``%gra`` (for dependency and grammatical relations), and other ``%`` tiers.
Much of what PyLangAcq can do relies on the annotations in these tiers with
rich linguistic information.


**Line continuations**

For any header and transcription lines that are too long, line continuations
are allowed in CHAT files with a tab character (denoted by ``<TAB>`` below), from::

    *XX1: this line is to demonstrate how line continuations are done in CHAT .

to::

    *XX1: this line is to demonstrate how line continuations
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
   The UTF-8 file encoding is assumed for all CHAT files.

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
    26980
    >>> eve.find_filename('eve01.cha')  # return the absolute path for a file basename
    '/home/joesmith/Brown/Eve/eve01.cha'

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
    26980
    >>> counts_by_files = eve.number_of_utterances(by_files=True)  # dict(filename: num of utterances)
    >>> import os
    >>> for abs_filename, n in sorted(counts_by_files.items()):
    ...     print(os.path.basename(abs_filename), n)
    ...
    eve01.cha 1601
    eve02.cha 1304
    eve03.cha 619
    eve04.cha 1456
    eve05.cha 1479
    eve06.cha 1075
    eve07.cha 1277
    eve08.cha 2058
    eve09.cha 1024
    eve10.cha 1060
    eve11.cha 952
    eve12.cha 1339
    eve13.cha 959
    eve14.cha 1094
    eve15.cha 1651
    eve16.cha 1500
    eve17.cha 2156
    eve18.cha 1760
    eve19.cha 1348
    eve20.cha 1268

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
    eve01.cha 749
    eve02.cha 488
    eve03.cha 253
    eve04.cha 590
    eve05.cha 707
    eve06.cha 542
    eve07.cha 528
    eve08.cha 959
    eve09.cha 521
    eve10.cha 547
    eve11.cha 447
    eve12.cha 648
    eve13.cha 460
    eve14.cha 476
    eve15.cha 724
    eve16.cha 641
    eve17.cha 904
    eve18.cha 791
    eve19.cha 653
    eve20.cha 539


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

    >>> corpus.add('Brown/Eve/eve0*.cha')  # from eve01.cha to eve09.cha
    >>> corpus.number_of_files()
    9

To remove transcripts with ``remove()``:

.. code-block:: python

    >>> corpus.remove('Brown/Eve/eve09.cha')
    >>> corpus.number_of_files()
    8

``update()`` takes a ``Reader`` instance and updates the current one:

.. code-block:: python

    >>> corpus.update(eve)  # 20 files from Eve
    >>> corpus.number_of_files()
    20
    >>> corpus.update(eve01)      # Trying to add duplicate files
    >>> corpus.number_of_files()  # does not result in errors or duplicates
    20
    >>> corpus.add('Brown/Adam/*.cha')  # Add 55 files, from adam01.cha to adam55.cha
    >>> corpus.number_of_files()
    75

``clear()`` applies to a ``Reader`` instance to clear everything and reset it
as an empty ``Reader`` instance:

.. code-block:: python

    >>> corpus.clear()
    >>> corpus.number_of_files()
    0
