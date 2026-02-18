.. _read:

Reading CHAT Data
=================

PyLangAcq is designed to handle conversational data represented in the CHAT format
as used in the TalkBank / CHILDES database for language acquisition research.
CHAT is documented in its `official manual <https://talkbank.org/0info/manuals/CHAT.pdf>`_.
This page describes the ways CHAT data can be read by the ``pylangacq`` package.


Initializing a CHAT Data Object
-------------------------------

:func:`~pylangacq.read_chat`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Reading CHAT data in PyLangAcq is all about creating a :class:`~pylangacq.CHAT` object.
The most convenient way to do it is to use the :func:`~pylangacq.read_chat` function,
which asks for a data source and several optional arguments.
As an example, let's use the `Brown <https://childes.talkbank.org/access/Eng-NA/Brown.html>`_
dataset of American English on CHILDES.
On this webpage, after you've logged in (account setup is free),
you should be able to download the full transcripts of CHAT data as a ZIP archive to your local drive.

.. code-block:: python

    import pylangacq
    brown = pylangacq.read_chat("path/to/your/local/Brown.zip")

:func:`~pylangacq.read_chat` automatically handles everything behind the scenes for you,
from unzipping the ZIP archive, traversing through the CHAT files found,
as well as parsing the files.
If the ZIP file has a fair amount of data
(the Brown dataset has over 200 CHAT data files, with over 180,000 utterances),
a :func:`~pylangacq.read_chat` call like this typically takes a couple seconds.

.. code-block:: python

    brown.info()
    # 214 files
    # 184635 utterances
    # 841281 words
    #     Utterance Count  Word Count  File Path            
    # --  ---------------  ----------  ---------------------
    # #1             1737        6328  Brown/Adam/020304.cha
    # #2             1972        7587  Brown/Adam/020318.cha
    # #3             1305        5431  Brown/Adam/020403.cha
    # #4             1224        4438  Brown/Adam/020415.cha
    # #5             1344        5375  Brown/Adam/020430.cha
    # ...
    # (set `verbose` to True for all the files)

For a quick preview of what the data looks like,
The :meth:`~pylangacq.CHAT.head` and :meth:`~pylangacq.CHAT.tail` methods
provide a quick preview of what the data looks like:

.. code-block:: python

    brown.head()
    # *CHI:   play                 checkers               .
    # %mor:   verb|play-Fin-Imp-S  noun|checker-Plur-Acc  .
    # %gra:   1|2|ROOT             2|1|OBJ                3|1|PUNCT
    # %xpho:  <1> pe

    # *CHI:  big         drum       .
    # %mor:  adj|big-S1  noun|drum  .
    # %gra:  1|2|AMOD    2|2|ROOT   3|2|PUNCT

    # *MOT:  big         drum       ?
    # %mor:  adj|big-S1  noun|drum  ?
    # %gra:  1|2|AMOD    2|2|ROOT   3|2|PUNCT

    # *CHI:  big         drum       .
    # %mor:  adj|big-S1  noun|drum  .
    # %gra:  1|2|AMOD    2|2|ROOT   3|2|PUNCT
    # %spa:  $IMIT

    # *CHI:  big         drum       .
    # %mor:  adj|big-S1  noun|drum  .
    # %gra:  1|2|AMOD    2|2|ROOT   3|2|PUNCT
    # %spa:  $IMIT

In practice, you likely only need a subset of the data at a time, e.g.,
focusing on a particular child. The Brown dataset contains data for the three children
Adam, Eve, and Sarah. Suppose you need Eve's data only.
:func:`~pylangacq.read_chat` takes the optional argument ``filter_files`` which, if specified,
filters the data down to the matching file paths.
To know what the file paths look like and therefore determine what the ``filter_files``
argument should be,
the ``brown`` CHAT reader we've just created
can tell you that via :meth:`~pylangacq.CHAT.file_paths`:

.. code-block:: python

    brown.file_paths
    # ['Brown/Adam/020304.cha',
    #  'Brown/Adam/020318.cha',
    #  ...
    #  'Brown/Eve/010600a.cha',
    #  'Brown/Eve/010600b.cha',
    #  ...
    #  'Brown/Sarah/020305.cha',
    #  'Brown/Sarah/020307.cha',
    #  ...
    #  'Brown/Sarah/050106.cha']

It looks like all and only Eve's data is inside the subdirectory called ``"Eve"``.
If we pass ``"Eve"`` to ``filter_files``, we should be getting only Eve's data this time:

.. code-block:: python

    eve = pylangacq.read_chat("path/to/your/local/Brown.zip", filter_files="Eve")
    eve.n_files
    # 20
    len(eve.utterances())
    # 26969

So far, we've seen how :func:`~pylangacq.read_chat` works with a local ZIP file.
Other data sources that this function is designed for are:

1. A directory (i.e., folder) on your local system,
   where CHAT data files are found immediately or recursively in subdirectories:

.. code-block:: python

    chat_data = pylangacq.read_chat("path/to/your/local/directory/")

2. A single CHAT file on your system:

.. code-block:: python

    chat_data = pylangacq.read_chat("path/to/your/local/data.cha")


:func:`~pylangacq.read_chat` is designed to cover the common use cases of reading in CHAT data.
Under the hood, it is a wrapper of several classmethods of :class:`~pylangacq.CHAT`,
some of which aren't available from :func:`~pylangacq.read_chat`.
These classmethods are introduced in the following.


From a ZIP File or Local Directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Perhaps you don't want :func:`~pylangacq.read_chat` to do the guess work of
what type of your data source is, or you want more fine-grained control
of what counts as CHAT data files or not in your data source.
While :func:`~pylangacq.read_chat` already handles a ZIP archive file and
a local directory, the :class:`~pylangacq.CHAT` classmethods
:meth:`~pylangacq.CHAT.from_zip` and :meth:`~pylangacq.CHAT.from_dir`
allow more optional arguments for customization.
Here's sample code for using these classmethods in the base case:

.. code-block:: python

    chat_data = pylangacq.CHAT.from_zip("path/to/your/local/data.zip")
    chat_data = pylangacq.CHAT.from_dir("path/to/your/local/directory/")


From Local CHAT Data Files
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you'd like to target specific CHAT files,
:meth:`~pylangacq.CHAT.from_files` takes a list of file paths:

.. code-block:: python

    path1 = "path/to/one/data/file.cha"
    path2 = "path/to/another/data/file.cha"
    chat_data = pylangacq.CHAT.from_files([path1, path2])


From In-Memory Strings
^^^^^^^^^^^^^^^^^^^^^^

If your CHAT data comes from in-memory strings,
:meth:`~pylangacq.CHAT.from_strs` takes a list of strings,
where each string is assumed to conform to the
`CHAT data format <https://talkbank.org/0info/manuals/CHAT.pdf>`_:

.. code-block:: python

    # Let's create some minimal CHAT data as a string.
    data = "*CHI:\tI want cookie .\n*MOT:\tokay ."

    # We should see two utterances.
    print(data)
    # *CHI:       I want cookie .
    # *MOT:       okay .

    chat_data = pylangacq.CHAT.from_strs([data])
    len(chat_data.utterances())
    # 2

    # All "file" terminology still applies.
    # Each CHAT data string you pass in is treated as one "file".
    chat_data.n_files
    # 1

    chat_data.utterances()
    # [Utterance(participant='CHI', tokens=[...4 tokens], time_marks=None),
    #  Utterance(participant='MOT', tokens=[...2 tokens], time_marks=None)]

We are getting ahead of ourselves by showing the result
of :meth:`~pylangacq.CHAT.utterances`.
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
:meth:`~pylangacq.CHAT.from_zip`,
:meth:`~pylangacq.CHAT.from_dir`,
:meth:`~pylangacq.CHAT.from_files`, and
:meth:`~pylangacq.CHAT.from_strs`,
and you may set it to ``False`` .


Creating an Empty CHAT Object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Calling :class:`~pylangacq.CHAT` itself with no arguments initializes an empty reader:

.. code-block:: python

    chat_data = pylangacq.CHAT()
    chat_data.n_files
    # 0

An empty data object is useful when you'd like to start with no data
and "grow" it by having data added as necessary.
The section below discusses how to manipulate a :class:`~pylangacq.CHAT` object.


Adding and Removing Data
------------------------

A :class:`~pylangacq.CHAT` keeps the linear ordering of CHAT data
by the ordering of the source data files.
CHAT data typically comes as data files that each represent a recording session.
There is, therefore, a natural ordering of the files by time,
for when the recordings were made.
The ordering is also commonly reflected by the way CHAT data files are named,
typically by the age of the target child.
For this reason, if your input data source is a ZIP file or local directory,
the resulting :class:`~pylangacq.CHAT` object has the data automatically sorted
based on file paths.

With the knowledge that data is ordered by files in a :class:`~pylangacq.CHAT`,
it is reasonable for a :class:`~pylangacq.CHAT` to append or drop data,
and to do so from either end for flexible data analysis and modeling.
Think of a :class:`~pylangacq.CHAT` object more or less like a double-ended queue.

The following :class:`~pylangacq.CHAT` methods support adding and removing data
(many of thenm inspired by :class:`~collections.deque`):

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    append
    append_left
    extend
    extend_left
    pop
    pop_left
    filter
    clear

Among these methods, :meth:`~pylangacq.CHAT.filter` creates and
returns a new :class:`~pylangacq.CHAT`
without altering the original one.
All the other methods work by mutating the calling :class:`~pylangacq.CHAT` in-place.

For convenience, the addition operator ``+`` is defined for :class:`~pylangacq.CHAT`
objects, and can be used to concatenate two :class:`~pylangacq.CHAT` objects.
By extension, ``+=`` is also valid, so a statement in the form of ``reader1 += reader2``
would mutate ``reader1`` by concatenating the two readers.

A :class:`~pylangacq.CHAT` can be iterated upon
(e.g., ``for reader_one_file in reader: ...``),
where the element in each iteration is a :class:`~pylangacq.CHAT` for one data file.
Slicing (``reader[:5]``, ``reader[3:6]``, etc) is also supported,
which gives you a :class:`~pylangacq.CHAT` object (which is iterable)
for the specified data files.
To inspect what data files are in a reader and their ordering
(as well as extract their indices, if necessary),
:meth:`~pylangacq.CHAT.file_paths` gives you the list of file paths.

The following example illustrates how to build a reader of Eve's utterances
starting from an empty one and adding data to it one file at a time.

.. code-block:: python

    new_chat = pylangacq.CHAT()  # empty CHAT object
    for eve_one_file in eve[:5]:
        new_chat += eve_one_file  # Note that new_chat is updated in-place.
        print(
            "Number of utterances so far:",
            len(new_chat.utterances()),
        )

    # Number of utterances so far: 1589
    # Number of utterances so far: 2879
    # Number of utterances so far: 3497
    # Number of utterances so far: 4950
    # Number of utterances so far: 6431

:meth:`~pylangacq.CHAT.filter` is designed to return
a new :class:`~pylangacq.CHAT`
so that we can instantiate a source :class:`~pylangacq.CHAT` for a TalkBank / CHILDES dataset
and filter it down to specific file paths or participants.
Typically, a dataset contains multiple participants' data
organized by a directory structure.
:meth:`~pylangacq.CHAT.filter` allows us to easily create :class:`~pylangacq.CHAT` objects
for individual children without re-loading data from scratch:

.. code-block:: python

    path = "path/to/your/local/Brown.zip"
    brown = pylangacq.read_chat(path)
    brown.n_files  # All CHAT files in the Brown dataset
    # 214

    # Eve's data is all Brown/Eve/*.cha -- match the "Eve" substring
    eve = brown.filter(files="Eve")
    eve.n_files
    # 20

    eve_chi = eve.filter(participants="CHI")  # child speech
    eve_chi.head()
    # *CHI:  more             cookie       .
    # %mor:  adj|more-Cmp-S1  noun|cookie  .
    # %gra:  1|2|AMOD         2|2|ROOT     3|2|PUNCT
    # %int:  distinctive , loud

    # *CHI:  more             cookie       .
    # %mor:  adj|more-Cmp-S1  noun|cookie  .
    # %gra:  1|2|AMOD         2|2|ROOT     3|2|PUNCT
    # %int:  distinctive , loud

    # *CHI:  more             juice       ?
    # %mor:  adj|more-Cmp-S1  noun|juice  ?
    # %gra:  1|2|AMOD         2|2|ROOT    3|2|PUNCT

    # *CHI:  Fraser        .
    # %mor:  propn|Fraser  .
    # %gra:  1|1|ROOT      2|1|PUNCT
    # %com:  pronounces Fraser as fr&jdij .

    # *CHI:  Fraser        .
    # %mor:  propn|Fraser  .
    # %gra:  1|1|ROOT      2|1|PUNCT


    eve_cds = eve.filter(participants="^(?!CHI$)")  # child-directed speech, regex ^(?!CHI$) for "not CHI"
    eve_cds.head()
    # *MOT:  you                  more             cookies           ?
    # %mor:  pron|you-Prs-Acc-S2  adj|more-Cmp-S1  noun|cookie-Plur  ?
    # %gra:  1|3|NSUBJ            2|3|AMOD         3|3|ROOT          4|3|PUNCT

    # *MOT:  how_about      another              graham        cracker       ?
    # %mor:  intj|howabout  det|another-Def-Ind  noun|graham   noun|cracker  ?
    # %gra:  1|4|DISCOURSE  2|4|DET              3|4|COMPOUND  4|4|ROOT      5|4|PUNCT

    # *MOT:  would            that           do             just        as          well       ?
    # %mor:  aux|would-Fin-S  pron|that-Dem  verb|do-Inf-S  adv|just    adv|as      adv|well   ?
    # %gra:  1|3|AUX          2|3|NSUBJ      3|6|ROOT       4|5|ADVMOD  5|3|ADVMOD  6|5|FIXED  7|3|PUNCT

    # *MOT:  here      .
    # %mor:  adv|here  .
    # %gra:  1|1|ROOT  2|1|PUNCT

    # *MOT:  here      you                  go                       .
    # %mor:  adv|here  pron|you-Prs-Nom-S2  verb|go-Fin-Ind-Pres-S2  .
    # %gra:  1|3|ROOT  2|3|NSUBJ            3|1|ADVCL-RELCL          4|1|PUNCT
