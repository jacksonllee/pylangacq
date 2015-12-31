.. _tutorial:

Tutorial
========

This page introduces the basic functionalities of PyLangAcq and points to
relevant pages of the library documentation for more advanced usage.

Testing the library installation
--------------------------------

To test that PyLangAcq is installed on your system, open your terminal with
your Python interpretor of choice (= the one for installing PyLangAcq)::

    >>> import pylangacq

If all goes well, there should be no import errors.

Getting CHAT data
-----------------

In this tutorial, we are going to explore some CHAT transcripts downloaded from
CHILDES. Specifically, let us assume that we have the `.cha` transcripts
for Eve from the Brown portion from
`here <http://childes.psy.cmu.edu/data/Eng-NA-MOR/Brown.zip>`_.

Let us further assume that there is a folder called ``data/`` at the current
directory, and we put the unzipped ``Brown/`` with all CHAT
transcripts inside ``data/``. This means the Eve data is now accessible
relative to the current directory::

    data/brown/Eve/<the twenty .cha transcripts for Eve>


Reading CHAT data
-----------------

To read the Eve data in PyLangAcq::

    >>> from pylangacq.chat import Reader
    >>> corpus = Reader('data/Brown/Eve/*')

The class ``Reader`` can read multiple CHAT files by
matching patterns with ``*`` (wildcard for zero or more characters) and
``?`` (wildcard for one character).
In this example, ``*`` matches all files (= the 20 CHAT files) for Eve::

    >>> corpus.number_of_files()
    20

More on :ref:`read`.

Accessing metadata
------------------

CHAT transcripts store metadata as headers with lines beginning with
``@``. For instance, we can retrieve the age information of the target child
in ``corpus`` created above::

    >>> from pprint import pprint
    >>> pprint(sorted(corpus.age().values()))
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

``corpus.age()`` returns a dict that maps a filename to the respective
file's age information (as a 3-tuple, e.g., ``(1, 6, 0)`` for 1 year and
6 months).

More on :ref:`metadata`.


Questions? Issues?
------------------

If you have any questions, comments, bug reports etc, please open issues
at the `GitHub repository <https://github.com/pylangacq/pylangacq>`_, or
contact `Jackson L. Lee <http://jacksonllee.com/>`_.

