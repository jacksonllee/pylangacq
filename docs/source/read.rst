.. _read:

Reading CHAT Data
=================

PyLangAcq is designed to handle conversational data represented in the CHAT format
as used in the CHILDES database for language acquisition research;
CHAT is documented in its `official manual <https://talkbank.org/manuals/CHAT.pdf>`_.
This page describes the ways CHAT data can be read by the ``pylangacq`` package.

Initializing a Reader
---------------------

:func:`~pylangacq.read_chat`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Reading CHAT data in PyLangAcq is all about creating a :class:`~pylangacq.Reader` object.
The most convenient way to do it is to use the :func:`~pylangacq.read_chat` function,
which asks for a data source and several optional arguments.
As an example, let's use the `Brown <https://childes.talkbank.org/access/Eng-NA/Brown.html>`_
dataset of American English on CHILDES:

.. invisible-code-block: python

    >>> import os, sys, pylangacq

.. skip: start if(os.getenv("CI") == "true" and sys.version_info[:2] == (3, 9), reason="py39 on CI doesn't work for unknown reason")

.. code-block:: python

    >>> import pylangacq
    >>> url = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"
    >>> brown = pylangacq.read_chat(url)

.. skip: end

If your data source is a URL pointing to a ZIP archive file, like the Brown
example here or many others from CHILDES,
:func:`~pylangacq.read_chat` automatically handles everything behind the scenes for you,
from downloading the ZIP file, unzipping it, traversing through the CHAT files found,
as well as parsing the files.
If the ZIP file has a fair amount of data
(the Brown dataset has over 200 CHAT data files, with over 180,000 utterances),
a :func:`~pylangacq.read_chat` call like this typically takes a couple seconds.

.. skip: start if(os.getenv("CI") == "true" and sys.version_info[:2] == (3, 9), reason="py39 on CI doesn't work for unknown reason")

.. code-block:: python

    >>> brown.n_files()
    214
    >>> len(brown.utterances())
    184639

.. skip: end

In practice, you likely only need a subset of the data at a time, e.g.,
focusing on a particular child. The Brown dataset contains data for the three children
Adam, Eve, and Sarah. Suppose you need Eve's data only.
:func:`~pylangacq.read_chat` takes the optional argument ``match`` which, if specified,
matches the file paths and only handles the matching data files.
To know what the file paths look like and therefore determine what the ``match`` argument should be,
either you independently have the unzipped files on your system
and see the subdirectory structure, or the ``brown`` reader we've just created
can tell you that via :func:`~pylangacq.Reader.file_paths`:

.. skip: start if(os.getenv("CI") == "true" and sys.version_info[:2] == (3, 9), reason="py39 on CI doesn't work for unknown reason")

.. code-block:: python

    >>> brown.file_paths()
    ['Brown/Adam/020304.cha',
     'Brown/Adam/020318.cha',
     ...
     'Brown/Eve/010600a.cha',
     'Brown/Eve/010600b.cha',
     ...
     'Brown/Sarah/020305.cha',
     'Brown/Sarah/020307.cha',
     ...
     'Brown/Sarah/050106.cha']

.. skip: end

It looks like all and only Eve's data is inside the subdirectory called ``"Eve"``.
If we pass ``"Eve"`` to ``match``, we should be getting only Eve's data this time
(and the function should run and finish noticeably faster due to the much smaller
data amount):

.. skip: start if(os.getenv("CI") == "true" and sys.version_info[:2] == (3, 9), reason="py39 on CI doesn't work for unknown reason")

.. code-block:: python

    >>> eve = pylangacq.read_chat(url, match="Eve")
    >>> eve.n_files()
    20
    >>> len(eve.utterances())
    26920

.. skip: end

So far, we've seen how :func:`~pylangacq.read_chat` works with a URL that points
to a ZIP file. Other data sources that this function is designed for are:

1. A ZIP file on your local system:

    .. skip: next

    .. code-block:: python

        >>> reader = pylangacq.read_chat("path/to/your/local/data.zip")

2. A directory (i.e., folder) on your local system, where CHAT data files are found immediately or recursively in subdirectories:

    .. skip: next

    .. code-block:: python

        >>> reader = pylangacq.read_chat("path/to/your/local/directory/")

3. A single CHAT file on your system:

    .. skip: next

    .. code-block:: python

        >>> reader = pylangacq.read_chat("path/to/your/local/data.cha")


:func:`~pylangacq.read_chat` is designed to cover the common use cases of reading in CHAT data.
Under the hood, it is a wrapper of several classmethods of :class:`~pylangacq.Reader`,
some of which aren't available from :func:`~pylangacq.read_chat`.
These classmethods are introduced in the following.


From a ZIP File or Local Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Perhaps you don't want :func:`~pylangacq.read_chat` to do the guess work of
what type of your data source is, or you want more fine-grained control
of what counts as CHAT data files or not in your data source.
While :func:`~pylangacq.read_chat` already handles a ZIP archive file and
a local directory, the :class:`~pylangacq.Reader` classmethods
:func:`~pylangacq.Reader.from_zip` and :func:`~pylangacq.Reader.from_dir`
allow more optional arguments for customization.
Here's sample code for using these classmethods in the base case:

    .. skip: start

    .. code-block:: python

        >>> reader = pylangacq.Reader.from_zip("path/to/your/local/data.zip")
        >>> reader = pylangacq.Reader.from_dir("path/to/your/local/directory/")

    .. skip: end

If you pass in a remote URL of a ZIP archive (``"https://.../some_data.zip"``) to
:func:`~pylangacq.Reader.from_zip`,
the downloaded data is cached on disk by default, so that the same data won't have
to be downloaded again for the same URL.
Setting the boolean keyword argument ``use_cached`` to ``False`` would force re-downloading.
The helper functions :func:`pylangacq.chat.cached_data_info` and
:func:`pylangacq.chat.remove_cached_data` let you check and remove cached data, respectively.


From Specific CHAT Data Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you'd like to target specific files, the :class:`~pylangacq.Reader` classmethod
:func:`~pylangacq.Reader.from_files` takes a list of file paths:

    .. skip: start

    .. code-block:: python

        >>> path1 = "path/to/one/data/file.cha"
        >>> path2 = "path/to/another/data/file.cha"
        >>> reader = pylangacq.Reader.from_files([path1, path2])

    .. skip: end


From In-Memory Strings
^^^^^^^^^^^^^^^^^^^^^^

If your CHAT data comes from in-memory strings,
the :class:`~pylangacq.Reader` classmethod
:func:`~pylangacq.Reader.from_strs` takes a list of strings,
where each string is assumed to conform to the
`CHAT data format <https://talkbank.org/manuals/CHAT.pdf>`_:

    .. code-block:: python

        >>> # Let's create some minimal CHAT data as a string.
        >>> data = "*CHI:\tI want cookie .\n*MOT:\tokay ."
        >>>
        >>> # We should see two utterances.
        >>> print(data)
        *CHI:       I want cookie .
        *MOT:       okay .
        >>>
        >>> reader = pylangacq.Reader.from_strs([data])
        >>> len(reader.utterances())
        2
        >>>
        >>> # All "file" terminology still applies.
        >>> # Each CHAT data string you pass in is treated as one "file".
        >>> reader.n_files()
        1
        >>>
        >>> reader.utterances()
        [Utterance(participant='CHI',
                   tokens=[Token(word='I', pos=None, mor=None, gra=None),
                           Token(word='want', pos=None, mor=None, gra=None),
                           Token(word='cookie', pos=None, mor=None, gra=None),
                           Token(word='.', pos=None, mor=None, gra=None)],
                   time_marks=None,
                   tiers={'CHI': 'I want cookie .'}),
         Utterance(participant='MOT',
                   tokens=[Token(word='okay', pos=None, mor=None, gra=None),
                           Token(word='.', pos=None, mor=None, gra=None)],
                   time_marks=None,
                   tiers={'MOT': 'okay .'})]

We are getting ahead of ourselves by showing the result
of the :class:`~pylangacq.Reader` classmethod :func:`~pylangacq.Reader.utterances`.
We are going to drill down to this and many other functions
in the upcoming parts of the documentation,
but this quick example gives you a glimpse of how PyLangAcq represents CHAT data.


Parallel Processing
^^^^^^^^^^^^^^^^^^^

Because a CHILDES / TalkBank dataset usually comes with multiple CHAT data files,
it is reasonable to parallelize the process of reading and parsing CHAT data for speed-up.
By default, such parallelization is applied.
If you would like to turn off parallel processing
(e.g., because your application is already parallelized, and further parallelization
from within PyLangAcq would create undesirable effects),
the boolean argument ``parallel`` is available at
:func:`~pylangacq.Reader.from_zip`,
:func:`~pylangacq.Reader.from_dir`,
:func:`~pylangacq.Reader.from_files`, and
:func:`~pylangacq.Reader.from_strs`,
and you may set it to ``False`` .


Creating an Empty Reader
^^^^^^^^^^^^^^^^^^^^^^^^

Calling :class:`~pylangacq.Reader` itself with no arguments initializes an empty reader:

.. code-block:: python

    >>> reader = pylangacq.Reader()
    >>> reader.n_files()
    0

An empty reader is useful when you'd like to start with no data
and "grow" the reader by having data added as necessary.
The section below discusses how to manipulate data in a reader.


Adding and Removing Data
------------------------

A :class:`~pylangacq.Reader` keeps the linear ordering of CHAT data
by the ordering of the source data files.
CHAT data typically comes as data files that each represent a recording session.
There is, therefore, a natural ordering of the files by time,
for when the recordings were made.
The ordering is also commonly reflected by the way CHAT data files are named.
For this reason, if your input data source is a ZIP file or local directory,
the resulting reader has the data automatically sorted based on file paths.

With the knowledge that data is ordered by files in a :class:`~pylangacq.Reader`,
it is reasonable for a :class:`~pylangacq.Reader` to append or drop data,
and to do so from either end for modeling purposes.
Think of a CHAT data reader more or less like a :class:`~collections.deque`.

The following :class:`~pylangacq.Reader` methods support adding and removing data
from a reader:

.. currentmodule:: pylangacq.Reader

.. autosummary::

    append
    append_left
    extend
    extend_left
    pop
    pop_left
    filter
    clear

Among these methods, :func:`~pylangacq.Reader.filter` creates and
returns a new :class:`~pylangacq.Reader`
without altering the original one.
All the other methods work by mutating the calling :class:`~pylangacq.Reader` in-place.

A :class:`~pylangacq.Reader` can be iterated upon
(e.g., ``for reader_one_file in reader: ...``),
where the element in each iteration is a :class:`~pylangacq.Reader` for one data file.
Slicing (``reader[:5]``, ``reader[3:6]``, etc) is also supported,
which gives you a :class:`~pylangacq.Reader` object (which is iterable)
for the specified data files.
To inspect what data files are in a reader and their ordering
(as well as extract their indices, if necessary),
:func:`~pylangacq.Reader.file_paths` gives you the list of file paths.

The following example illustrates how to build a reader of Eve's utterances
starting from an empty one and adding data to it one file at a time.

.. skip: start if(os.getenv("CI") == "true" and sys.version_info[:2] == (3, 9), reason="py39 on CI doesn't work for unknown reason")

.. code-block:: python

    >>> reader = pylangacq.Reader()  # an empty reader
    >>> for eve_one_file in eve[:5]:
    ...     reader.append(eve_one_file)
    ...     print(
    ...         "Number of Eve's utterances in the reader so far:",
    ...         len(reader.utterances(participants='CHI'))
    ...     )
    ...
    Number of Eve's utterances in the reader so far: 741
    Number of Eve's utterances in the reader so far: 1214
    Number of Eve's utterances in the reader so far: 1467
    Number of Eve's utterances in the reader so far: 2052
    Number of Eve's utterances in the reader so far: 2758

.. skip: end

:func:`~pylangacq.Reader.filter` is designed to explicitly return
a new :class:`~pylangacq.Reader`
so that we can instantiate a source :class:`~pylangacq.Reader` for a CHILDES / TalkBank dataset
and filter it down to specific file paths to get smaller :class:`~pylangacq.Reader` objects.
Typically, a CHILDES dataset contains multiple children's data
organized by a subdirectory structure.
:func:`~pylangacq.Reader.filter` allows us to easily create :class:`~pylangacq.Reader` objects
for individual children without re-downloading data:

.. skip: start if(os.getenv("CI") == "true" and sys.version_info[:2] == (3, 9), reason="py39 on CI doesn't work for unknown reason")

.. code-block:: python

    >>> url = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"
    >>> brown = pylangacq.read_chat(url)
    >>> len(brown.file_paths())  # All CHAT files in the Brown dataset
    214
    >>>
    >>> # Eve's data is all Brown/Eve/*.cha -- match the "Eve" substring
    >>> eve = brown.filter(match="Eve")
    >>> len(eve.file_paths())  # Only the 20 CHAT files for Eve
    20
    >>> eve.file_paths()[:3]
    ['Brown/Eve/010600a.cha', 'Brown/Eve/010600b.cha', 'Brown/Eve/010700a.cha']
    >>>
    >>> # Sarah's data is all Brown/Sarah/*.cha -- match the "Sarah" substring
    >>> sarah = brown.filter(match="Sarah")
    >>> len(sarah.file_paths())  # Only the 139 CHAT files for Sarah
    139
    >>> sarah.file_paths()[:3]
    ['Brown/Sarah/020305.cha', 'Brown/Sarah/020307.cha', 'Brown/Sarah/020319.cha']

.. skip: end

Custom Behavior
---------------

If custom behavior in CHAT handling is needed,
consider defining a child class that inherits from :class:`~pylangacq.Reader`.
This approach is suitable if, for instance, new class methods are needed,
or the words / tokens / utterances need a custom treatment during CHAT parsing.
As long as you have conversational data formatted in CHAT
(data not necessarily from CHILDES or TalkBank,
and not necessarily for language acquisition research, either),
subclassing from :class:`~pylangacq.Reader` is a powerful way to
modify and extend the CHAT handling capabilities.
As an example, please see the class :class:`~pycantonese.CHATReader`
for Cantonese conversational data in the
`PyCantonese <https://pycantonese.org>`_ package.
