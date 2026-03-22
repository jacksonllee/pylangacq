.. _headers:

Accessing Headers
=================

CHAT data files record metadata such as the participants' demographic information
in a header section, which has lines starting with the ``@`` character
and is typically found at the top of a data file.
The following is the header section of ``Brown/Eve/010600a.cha`` from CHILDES:

.. code-block::

    @UTF8
    @PID:	11312/c-00034743-1
    @Begin
    @Languages:	eng
    @Participants:	CHI Target_Child , MOT Mother , COL Investigator , RIC Investigator
    @ID:	eng|Brown|CHI|1;06.00|female|||Target_Child|||
    @ID:	eng|Brown|MOT||female|||Mother|||
    @ID:	eng|Brown|COL|||||Investigator|||
    @ID:	eng|Brown|RIC|||||Investigator|||
    @Date:	15-OCT-1962
    @Time Duration:	10:00-11:00
    @Types:	long , toyplay , TD


:class:`~pylangacq.CHAT` has the following methods
to access the commonly needed information from the headers:

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    ages
    headers
    languages
    participants


Let's use Eve's data to see these methods in action.

.. code-block:: python

    import pylangacq
    path = "path/to/your/local/Brown.zip"
    eve = pylangacq.read_chat(path, filter_files="Eve")

Ages
----

:meth:`~pylangacq.CHAT.ages` returns the age information of the participant ``"CHI"``
-- typically, only the age of the target child is available.

:meth:`~pylangacq.CHAT.ages` understands CHAT's age format that looks like ``1;06.00``
(= one year, six months, and zero days old)
and wraps it in a helper class :class:`~pylangacq.Age`:

.. code-block:: python

    eve.ages()
    # [Age('1;06.00'),
    #  Age('1;06.00'),
    #  Age('1;07.00'),
    #  Age('1;07.00'),
    #  Age('1;08.00'),
    #  Age('1;09.00'),
    #  Age('1;09.00'),
    #  Age('1;09.00'),
    #  Age('1;10.00'),
    #  Age('1;10.00'),
    #  Age('1;11.00'),
    #  Age('1;11.00'),
    #  Age('2;00.00'),
    #  Age('2;00.00'),
    #  Age('2;01.00'),
    #  Age('2;01.00'),
    #  Age('2;02.00'),
    #  Age('2;02.00'),
    #  Age('2;03.00'),
    #  Age('2;03.00')]

:class:`~pylangacq.Age` has the method :meth:`~pylangacq.Age.in_months`
for converting the age information into months
(as floats, useful for downstream data analyses and making plots):

.. code-block:: python

    [age.in_months() for age in eve.ages()]
    # [18.0,
    #  18.0,
    #  19.0,
    #  19.0,
    #  20.0,
    #  21.0,
    #  21.0,
    #  21.0,
    #  22.0,
    #  22.0,
    #  23.0,
    #  23.0,
    #  24.0,
    #  24.0,
    #  25.0,
    #  25.0,
    #  26.0,
    #  26.0,
    #  27.0,
    #  27.0]


Languages
---------

:meth:`~pylangacq.CHAT.languages` returns the language information.
Eve's data is naturally in English.
In datasets with more than one language (bi-/multilingualism),
the ``by_file=True`` flag would indicate the languages in individual files according to
the headers.

.. code-block:: python

    eve.languages()
    # ['eng']


Participants
------------

:meth:`~pylangacq.CHAT.participants` returns the participants (e.g., ``"CHI"``)
in the data. ``by_file=True`` is also available if you need the information
by individual files.

.. code-block:: python

    eve.participants(by_file=True)  # a list of lists of Participant objects
    # [[Participant(code='CHI', name='', role='Target_Child'),
    #   Participant(code='MOT', name='', role='Mother'),
    #   Participant(code='COL', name='', role='Investigator'),
    #   Participant(code='RIC', name='', role='Investigator')],
    #   ...
    #  ]

Each participant has their information available via attributes through the helper class
:class:`~pylangacq.Participant`. For instance:

.. code-block:: python

    chi = eve.participants(by_file=True)[0][0]
    chi
    # Participant(code='CHI', name='', role='Target_Child')
    chi.age
    # Age('1;06.00')
    chi.role
    # 'Target_Child'


Other Header Information
------------------------

For any header information not given by one of the implemented methods above,
:meth:`~pylangacq.CHAT.headers` gives a list of headers,
where each header is a :class:`~pylangacq.Headers` object for each data file,
and you can walk through the object for information you need.

.. code-block:: python

    headers = eve.headers()  # a list of Headers objects
    headers[0]
    # Headers(languages=["eng"], participants=[...4], date=datetime.date(1962, 10, 15))

See the documentation of :class:`~pylangacq.Headers` for more details.
