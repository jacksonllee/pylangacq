.. _metadata:

Accessing metadata
==================

A ``Reader`` object has an array of methods for accessing metadata
(based on headers given by the ``@`` lines) and data
(the transcriptions with ``*`` and dependent tiers with ``%``).
This page introduces the metadata methods.
For data methods, see :ref:`transcriptions`.
For details of the ``Reader`` class, see :ref:`reader_api`.

Metadata methods for handling information from the ``@`` headers:

========================  =========================================================================================
Method                    Return object
========================  =========================================================================================
``participant_codes()``   set of participant codes across all files; if ``by_file`` is ``True``, then dict(filename: set of participant codes) instead
``participants()``        dict(filename: dict(participant code: dict of the ``@ID`` information for that participant))
``age()``                 dict(filename: tuple of (*years*, *months*, *days*))
``languages()``           dict(filename: list of languages based on the ``@Languages`` header)
``dates_of_recording()``  dict(filename: list(tuple of (*year*, *month*, *day*)))
``headers()``             dict(filename: dict(header name: the content of that header))
========================  =========================================================================================

Among these methods, only ``participant_codes()`` has the optional parameter
``by_files``.

To illustrate metadata access methods, it is helpful to be familiar with what
the headers (= the lines beginning with ``@``) look like in a CHAT transcript
such as ``eve01.cha``::

    @UTF8
    @PID:	11312/c-00034743-1
    @Begin
    @Languages:	eng
    @Participants:	CHI Eve Target_Child , MOT Sue Mother , COL Colin Investigator , RIC Richard Investigator
    @ID:	eng|Brown|CHI|1;6.|female|||Target_Child|||
    @ID:	eng|Brown|MOT|||||Mother|||
    @ID:	eng|Brown|COL|||||Investigator|||
    @ID:	eng|Brown|RIC|||||Investigator|||
    @Date:	15-OCT-1962
    @Time Duration:	10:00-11:00

Using the metadata access methods:

.. code-block:: python

    >>> from pprint import pprint
    >>> import pylangacq as pla
    >>> eve = pla.read_chat('Brown/Eve/*.cha')
    >>> eve01_filename = eve.abspath('010600a.cha')  # get the absolute path of Eve's first data file
    >>> eve.participant_codes()  # across all 20 files
    {'RIC', 'COL', 'URS', 'FAT', 'GLO', 'CHI', 'MOT'}
    >>> eve.participant_codes(by_files=True)[eve01_filename]  # only for 010600a.cha
    {'COL', 'CHI', 'MOT', 'RIC'}
    >>> pprint(eve.participants()[eve01_filename])
    {'CHI': {'SES': '',
             'age': '1;6.',
             'corpus': 'Brown',
             'custom': '',
             'education': '',
             'group': '',
             'language': 'eng',
             'participant_name': 'Eve',
             'participant_role': 'Target_Child',
             'sex': 'female'},
     'COL': {'SES': '',
             'age': '',
             'corpus': 'Brown',
             'custom': '',
             'education': '',
             'group': '',
             'language': 'eng',
             'participant_name': 'Colin',
             'participant_role': 'Investigator',
             'sex': ''},
     'MOT': {'SES': '',
             'age': '',
             'corpus': 'Brown',
             'custom': '',
             'education': '',
             'group': '',
             'language': 'eng',
             'participant_name': 'Sue',
             'participant_role': 'Mother',
             'sex': ''},
     'RIC': {'SES': '',
             'age': '',
             'corpus': 'Brown',
             'custom': '',
             'education': '',
             'group': '',
             'language': 'eng',
             'participant_name': 'Richard',
             'participant_role': 'Investigator',
             'sex': ''}}
    >>> eve.age()[eve01_filename]  # defaults to the target child's age; (years, months, days)
    (1, 6, 0)
    >>> eve.age(months=True)[eve01_filename]  # target child's age in months
    18.0
    >>> eve.age(participant='MOT')[eve01_filename]  # no age info for MOT
    (0, 0, 0)
    >>> eve.languages()[eve01_filename]  # list but not set; ordering matters in bi/multilingualism
    ['eng']
    >>> eve.dates_of_recording()[eve01_filename]  # some CHAT files have multiple dates
    [(1962, 10, 15), (1962, 10, 17)]

If the CHAT file has headers that are not covered by specific built-in
methods illustrated above, they are always accessible with ``headers()``:

.. code-block:: python

    >>> pprint(eve.headers()[eve01_filename])
    {'Date': ['15-OCT-1962', '17-OCT-1962'],
     'Languages': 'eng',
     'PID': '11312/c-00034743-1',
     'Participants': {'CHI': {'SES': '',
                              'age': '1;6.0',
                              'corpus': 'Brown',
                              'custom': '',
                              'education': '',
                              'group': '',
                              'language': 'eng',
                              'participant_name': 'Eve',
                              'participant_role': 'Target_Child',
                              'sex': 'female'},
                      'COL': {'SES': '',
                              'age': '',
                              'corpus': 'Brown',
                              'custom': '',
                              'education': '',
                              'group': '',
                              'language': 'eng',
                              'participant_name': 'Colin',
                              'participant_role': 'Investigator',
                              'sex': ''},
                      'MOT': {'SES': '',
                              'age': '',
                              'corpus': 'Brown',
                              'custom': '',
                              'education': '',
                              'group': '',
                              'language': 'eng',
                              'participant_name': 'Sue',
                              'participant_role': 'Mother',
                              'sex': ''},
                      'RIC': {'SES': '',
                              'age': '',
                              'corpus': 'Brown',
                              'custom': '',
                              'education': '',
                              'group': '',
                              'language': 'eng',
                              'participant_name': 'Richard',
                              'participant_role': 'Investigator',
                              'sex': ''}},
     'Tape Location': '850',
     'Time Duration': '11:30-12:00',
     'UTF8': ''}
