.. _write:

Writing CHAT Data
=================

To output CHAT data, a :class:`~pylangacq.Reader` object can either export data to local files
or write its data to strings.

.. currentmodule:: pylangacq.Reader

.. autosummary::

    to_chat
    to_strs

These methods are useful for saving CHAT data for re-use or distribution,
especially when your data or :class:`~pylangacq.Reader` object is customized in some way,
e.g., by adding or removing data from an existing dataset, or through
an in-memory CHAT data string -- see :ref:`read`.

.. skip: start

.. code-block:: python

    >>> import pylangacq
    >>> reader = pylangacq.Reader.from_strs(["*MOT: hey sweetie ."])
    >>> reader.to_chat("data.cha")

.. skip: end

If your :class:`~pylangacq.Reader` object has data organized in multiple CHAT files,
:func:`~pylangacq.Reader.to_chat` supports writing CHAT data files in a local directory:

.. skip: start

.. code-block:: python

    >>> import pylangacq
    >>> brown = pylangacq.read_chat("https://childes.talkbank.org/data/Eng-NA/Brown.zip")
    >>> # Brown has data for Adam, Eve, and Sarah.
    >>> # Now we want to save only Eve and Sarah's data somewhere on disk.
    >>> eve_and_sarah = brown.filter(exclude="Adam")
    >>> eve_and_sarah.to_chat("your/new/directory", is_dir=True)

.. skip: end

By default, the files are named ``0001.cha``, ``0002.cha``, etc.
To customize the filenames,
:func:`~pylangacq.Reader.to_chat` has the ``filenames`` keyword argument.

If you would like the CHAT data as strings in memory for use cases other than
local file export,
:func:`~pylangacq.Reader.to_strs` is available.
