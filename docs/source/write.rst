.. _write:

Writing CHAT Data
=================

To write CHAT data, a :class:`~pylangacq.Reader` object can either write its data
to CHAT data strings or export data to CHAT files.

.. currentmodule:: pylangacq.Reader

.. autosummary::

    to_strs
    to_chat

These methods are useful for saving CHAT data for re-use or distribution,
especially when your data or :class:`~pylangacq.Reader` object is customized in some way,
e.g., by adding or removing data from an existing dataset, or through
an in-memory CHAT data string -- see :ref:`read`.

:func:`~pylangacq.Reader.to_chat` writes CHAT data files in a local directory.

.. skip: start

.. code-block:: python

    >>> import pylangacq
    >>> brown = pylangacq.read_chat("https://childes.talkbank.org/data/Eng-NA/Brown.zip")
    >>> # Brown has data for Adam, Eve, and Sarah.
    >>> # Now we want to save only Eve and Sarah's data somewhere on disk.
    >>> eve_and_sarah = brown.filter(exclude="Adam")
    >>> eve_and_sarah.to_chat("your/new/directory")

.. skip: end

By default, the files are named ``0001.cha``, ``0002.cha``, etc.
To customize the filenames,
:func:`~pylangacq.Reader.to_chat` has the ``filenames`` keyword argument.

If you would like the CHAT data as strings in memory for use cases other than
local file export,
:func:`~pylangacq.Reader.to_strs` is available.
