.. _write:

Writing CHAT Data
=================

To output CHAT data, a :class:`~pylangacq.CHAT` object can either export data to local files
or write its data to strings.

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    to_files
    to_strs

These methods are useful for saving CHAT data for re-use or distribution,
especially when your data or :class:`~pylangacq.CHAT` object is customized in some way,
e.g., by adding or removing data from an existing dataset, or through
an in-memory CHAT data string -- see :ref:`read`.

.. code-block:: python

    import pylangacq
    chat_data = pylangacq.CHAT.from_strs(["*MOT:\they sweetie ."])
    chat_data.to_files("output_dir/")

If your :class:`~pylangacq.CHAT` object has data organized in multiple CHAT files,
:meth:`~pylangacq.CHAT.to_files` writes them all to the given directory:

.. code-block:: python

    import pylangacq
    brown = pylangacq.read_chat("path/to/your/local/Brown.zip")
    # Brown has data for Adam, Eve, and Sarah.
    # Now we want to save only Eve and Sarah's data somewhere on disk.
    eve_and_sarah = brown.filter(files="Eve|Sarah")
    eve_and_sarah.to_files("your/new/directory")

By default, filenames are derived from the original source file paths
(e.g., ``foo.cha`` stays ``foo.cha``).
If the data was parsed from in-memory strings without explicit IDs,
numbered names are used (``0001.cha``, ``0002.cha``, etc.).
To override, use the ``filenames`` keyword argument of
:meth:`~pylangacq.CHAT.to_files`.

If you would like the CHAT data as strings in memory for use cases other than
local file export,
:meth:`~pylangacq.CHAT.to_strs` is available.
