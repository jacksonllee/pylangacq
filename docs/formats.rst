.. _formats:

Format Conversion
=================

The :class:`~pylangacq.CHAT` class can convert CHAT data to other annotation formats.

CHAT to ELAN
-------------

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    to_elan
    to_elan_files
    to_elan_strs

:meth:`~pylangacq.CHAT.to_elan` converts CHAT data to an
:class:`~rustling.elan.ELAN` object.
Each CHAT file produces one ELAN file.

**Tier mapping:**

- Each CHAT participant (e.g., ``*CHI:``, ``*MOT:``) becomes an
  **alignable** (time-aligned, parent) tier in ELAN, with the tier ID
  set to the participant code (e.g., ``CHI``, ``MOT``).
- Each CHAT dependent tier (e.g., ``%mor``, ``%gra``, ``%gpx``) becomes
  a **reference annotation** (child) tier in ELAN, with the tier ID
  ``{tier}@{participant}`` (e.g., ``mor@CHI``, ``gra@MOT``).
- If the CHAT file has an ``@Media`` header, an ELAN ``MEDIA_DESCRIPTOR``
  element is included.

**Example:**

.. code-block:: python

    import pylangacq

    chat = pylangacq.read_chat("path/to/your/data.cha")

    # Convert to an ELAN object
    elan = chat.to_elan()

    # Write .eaf files to a directory
    chat.to_elan_files("output_dir/")

    # With custom filenames
    chat.to_elan_files("output_dir/", filenames=["alice.eaf", "bob.eaf"])

To get EAF XML strings in memory (e.g., for inspection or further processing),
use :meth:`~pylangacq.CHAT.to_elan_strs`:

.. code-block:: python

    eaf_strings = chat.to_elan_strs()

The resulting :class:`~rustling.elan.ELAN` object (or .eaf files) can be opened in
`ELAN <https://archive.mpi.nl/tla/elan>`_
or further processed with :class:`rustling.elan.ELAN`.

CHAT to TextGrid
-----------------

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    to_textgrid
    to_textgrid_files
    to_textgrid_strs

:meth:`~pylangacq.CHAT.to_textgrid` converts CHAT data to a
:class:`~rustling.textgrid.TextGrid` object.
Each CHAT file produces one TextGrid file.

**Mapping:**

- Each CHAT participant becomes an IntervalTier (tier name = participant code).
- Utterances without time marks are skipped.
- Times are converted from milliseconds to seconds.

**Participant selection:**

By default, all participants are included.
To select specific participants, pass the ``participants`` keyword argument:

.. code-block:: python

    import pylangacq

    chat = pylangacq.read_chat("path/to/your/data.cha")

    # Convert to a TextGrid object
    textgrid = chat.to_textgrid()

    # Only include specific participants
    textgrid = chat.to_textgrid(participants=["CHI"])

    # Write .TextGrid files to a directory
    chat.to_textgrid_files("output_dir/")

    # With custom filenames
    chat.to_textgrid_files("output_dir/", filenames=["child.TextGrid"])

To get TextGrid strings in memory, use :meth:`~pylangacq.CHAT.to_textgrid_strs`:

.. code-block:: python

    textgrid_strings = chat.to_textgrid_strs()

The resulting :class:`~rustling.textgrid.TextGrid` object (or .TextGrid files)
can be opened in `Praat <https://www.fon.hum.uva.nl/praat/>`_.

CHAT to CoNLL-U
----------------

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    to_conllu
    to_conllu_files
    to_conllu_strs

:meth:`~pylangacq.CHAT.to_conllu` converts CHAT data to a
:class:`~rustling.conllu.CoNLLU` object.
Each CHAT file produces one CoNLL-U file, with each utterance becoming one sentence.

**Mapping:**

- Each CHAT utterance becomes one CoNLL-U sentence.
- ``Token.word`` maps to FORM.
- ``Token.pos`` (from ``%mor``) maps to UPOS.
- ``Token.mor`` (from ``%mor``) maps to LEMMA.
- ``Token.gra`` (from ``%gra``) maps to HEAD and DEPREL.
- Fields without a direct mapping (XPOS, FEATS, DEPS, MISC) are set to ``_``.

**Example:**

.. code-block:: python

    import pylangacq

    chat = pylangacq.read_chat("path/to/your/data.cha")

    # Convert to a CoNLL-U object
    conllu = chat.to_conllu()

    # Write .conllu files to a directory
    chat.to_conllu_files("output_dir/")

    # With custom filenames
    chat.to_conllu_files("output_dir/", filenames=["output.conllu"])

To get CoNLL-U strings in memory, use :meth:`~pylangacq.CHAT.to_conllu_strs`:

.. code-block:: python

    conllu_strings = chat.to_conllu_strs()

The resulting :class:`~rustling.conllu.CoNLLU` object (or .conllu files)
can be used with `Universal Dependencies <https://universaldependencies.org/>`_ tools.

CHAT to SRT
------------

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    to_srt
    to_srt_files
    to_srt_strs

:meth:`~pylangacq.CHAT.to_srt` converts CHAT data to an
:class:`~rustling.srt.SRT` object.
Each CHAT file produces one SRT file.

**Mapping:**

- Each CHAT utterance with time marks becomes one subtitle block.
- Utterances without time marks are skipped (SRT requires time ranges).
- When multiple participants are present, the subtitle text is prefixed
  with the participant code (e.g., ``"CHI: more cookie ."``).
  For a single participant, no prefix is added.

**Participant selection:**

By default, all participants are included.
To select specific participants, pass the ``participants`` keyword argument:

.. code-block:: python

    import pylangacq

    chat = pylangacq.read_chat("path/to/your/data.cha")

    # Convert to an SRT object
    srt = chat.to_srt()

    # Only include specific participants
    srt = chat.to_srt(participants=["CHI"])

    # Write .srt files to a directory
    chat.to_srt_files("output_dir/")

    # With custom filenames
    chat.to_srt_files("output_dir/", filenames=["child.srt"])

To get SRT strings in memory (e.g., for inspection or further processing),
use :meth:`~pylangacq.CHAT.to_srt_strs`:

.. code-block:: python

    srt_strings = chat.to_srt_strs()

The resulting :class:`~rustling.srt.SRT` object (or .srt files)
can be opened in any media player or subtitle editor.
