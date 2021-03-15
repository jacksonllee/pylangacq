.. _headers:

Accessing Headers
=================

CHAT data files record metadata such as the participants' demographic information
in a header section, which has lines starting with the ``@`` character
and is typically found at the top of a data file.
The following is the header section of ``Brown/Eve/010600a.cha`` from CHILDES:

.. skip: start

.. code-block::

    @UTF8
    @PID:	11312/c-00034743-1
    @Begin
    @Languages:	eng
    @Participants:	CHI Eve Target_Child , MOT Sue Mother , COL Colin Investigator , RIC Richard Investigator
    @ID:	eng|Brown|CHI|1;06.00|female|||Target_Child|||
    @ID:	eng|Brown|MOT||female|||Mother|||
    @ID:	eng|Brown|COL|||||Investigator|||
    @ID:	eng|Brown|RIC|||||Investigator|||
    @Date:	15-OCT-1962

.. skip: end

:class:`~pylangacq.chat.Reader` has the following methods
to access the commonly needed information from the headers:

.. currentmodule:: pylangacq.Reader

.. autosummary::

    ages
    dates_of_recording
    headers
    languages
    participants


Let's use Eve's data to see these methods in action.

.. code-block:: python

    >>> import pylangacq
    >>> url = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"
    >>> eve = pylangacq.read_chat(url, "Eve")

Ages
----

:func:`~pylangacq.Reader.ages` returns the age information of the participant ``"CHI"``
(the target child) by default, since CHAT is by far most commonly used
in language acquisition and development research, and that typically only the age of the
target child is available. The only argument ``participant`` can be passed in
if your use case is not the target child.

:func:`~pylangacq.Reader.ages` understands the age format that looks like ``1;06.00``
and gives you a tuple of three integers
such as ``(1, 6, 0)`` for one year, six months, and zero days old.

.. code-block:: python

    >>> eve.ages()
    [(1, 6, 0),
     (1, 6, 0),
     (1, 7, 0),
     (1, 7, 0),
     (1, 8, 0),
     (1, 9, 0),
     (1, 9, 0),
     (1, 9, 0),
     (1, 10, 0),
     (1, 10, 0),
     (1, 11, 0),
     (1, 11, 0),
     (2, 0, 0),
     (2, 0, 0),
     (2, 1, 0),
     (2, 1, 0),
     (2, 2, 0),
     (2, 2, 0),
     (2, 3, 0),
     (2, 3, 0)]

Passing in ``months=True`` converts the ages into months:

.. code-block:: python

    >>> eve.ages(months=True)
    [18.0,
     18.0,
     19.0,
     19.0,
     20.0,
     21.0,
     21.0,
     21.0,
     22.0,
     22.0,
     23.0,
     23.0,
     24.0,
     24.0,
     25.0,
     25.0,
     26.0,
     26.0,
     27.0,
     27.0]


Dates of Recording
------------------

:func:`~pylangacq.Reader.dates_of_recording` returns the dates of recording
as a set of :class:`~datetime.date` objects
for all the date files.

Some files have the same dates, as multiple recording sessions were conducted
on the same day. To have the dates by data files,
passing in ``by_files=True`` gives you a list of sets of :class:`~datetime.date`s,
where each set is for one file:

.. skip: start

.. code-block:: python

    >>> eve.dates_of_recording(by_files=True)
    [{datetime.date(1962, 10, 15), datetime.date(1962, 10, 17)},
     {datetime.date(1962, 10, 31), datetime.date(1962, 10, 29)},
     {datetime.date(1962, 11, 12)},
     {datetime.date(1962, 11, 28), datetime.date(1962, 11, 26)},
     {datetime.date(1962, 12, 10), datetime.date(1962, 12, 12)},
     {datetime.date(1963, 1, 2), datetime.date(1962, 12, 31)},
     {datetime.date(1963, 1, 14), datetime.date(1963, 1, 16)},
     {datetime.date(1963, 1, 28)},
     {datetime.date(1963, 2, 11), datetime.date(1963, 2, 13)},
     {datetime.date(1963, 2, 25), datetime.date(1963, 2, 27)},
     {datetime.date(1963, 3, 11), datetime.date(1963, 3, 13)},
     {datetime.date(1963, 3, 25),
      datetime.date(1963, 3, 26),
      datetime.date(1963, 3, 27)},
     {datetime.date(1963, 4, 15)},
     {datetime.date(1963, 5, 1), datetime.date(1963, 4, 29)},
     {datetime.date(1963, 5, 15), datetime.date(1963, 5, 13)},
     {datetime.date(1963, 5, 27), datetime.date(1963, 5, 28)},
     {datetime.date(1963, 6, 10), datetime.date(1963, 6, 11)},
     {datetime.date(1963, 6, 26), datetime.date(1963, 6, 24)},
     {datetime.date(1963, 7, 3), datetime.date(1963, 7, 12)},
     {datetime.date(1963, 7, 23)}]

.. skip: end

Languages
---------

:func:`~pylangacq.Reader.languages` returns the language information.
Eve's data is naturally in English.
In datasets with more than one language (bi-/multilingualism),
the ``by_files=True`` flag would indicate the languages in individual files according to
the headers.

.. code-block:: python

    >>> eve.languages()
    {'eng'}


Participants
------------

:func:`~pylangacq.Reader.participants` returns the participants (e.g., ``"CHI"``, ``"MOT"``)
in the reader. ``by_files=True`` is also available if you need the information
by individual files.

.. skip: start

.. code-block:: python

    >>> eve.participants()
    {'URS', 'CHI', 'MOT', 'FAT', 'RIC', 'COL', 'GLO'}

.. skip: end

The more detailed information for each participant
(e.g., gender, role in recording) can be retrieved from :func:`~pylangacq.Reader.headers`,
which is illustrated next.

Other Header Information
------------------------

For any header information not given by one of the implemented methods above,
:func:`~pylangacq.Reader.headers` gives a list of headers,
where each header is a generic Python dictionary for each data file,
and you can walk through the dict for information you need.

.. skip: start

.. code-block:: python

    >>> headers = eve.headers()  # a list of dicts
    >>> headers[0]  # show the header of Brown/Eve/010600a.cha
    {'Date': {datetime.date(1962, 10, 15), datetime.date(1962, 10, 17)},
     'Languages': ['eng'],
     'PID': '11312/c-00034743-1',
     'Participants': {'CHI': {'age': '1;06.00',
                              'corpus': 'Brown',
                              'custom': '',
                              'education': '',
                              'group': '',
                              'language': 'eng',
                              'name': 'Eve',
                              'role': 'Target_Child',
                              'ses': '',
                              'sex': 'female'},
                      'COL': {'age': '',
                              'corpus': 'Brown',
                              'custom': '',
                              'education': '',
                              'group': '',
                              'language': 'eng',
                              'name': 'Colin',
                              'role': 'Investigator',
                              'ses': '',
                              'sex': ''},
                      'MOT': {'age': '',
                              'corpus': 'Brown',
                              'custom': '',
                              'education': '',
                              'group': '',
                              'language': 'eng',
                              'name': 'Sue',
                              'role': 'Mother',
                              'ses': '',
                              'sex': 'female'},
                      'RIC': {'age': '',
                              'corpus': 'Brown',
                              'custom': '',
                              'education': '',
                              'group': '',
                              'language': 'eng',
                              'name': 'Richard',
                              'role': 'Investigator',
                              'ses': '',
                              'sex': ''}},
     'Tape Location': '850',
     'Time Duration': '11:30-12:00',
     'Types': 'long, toyplay, TD',
     'UTF8': ''}

.. skip: end
