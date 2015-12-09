PyLangAcq: Language acquisition research in Python
==================================================

What is this
------------

PyLangAcq is a Python library for the computational modeling of language acquisition. The library is under active development. The current version is 0.3.

Currently, the focus is to develop capabilities to interface with `.cha` transcription files in the CHAT format, widely used by the [CHILDES](http://childes.psy.cmu.edu/) database.

As the CHAT format is used for conversation transcriptions more generally, researchers whose work is concerned with transcribed speech, conversation analysis, and other related areas will also benefit from this library.

Download and install
--------------------

PyLangAcq is currently available through GitHub:

    $ git clone https://github.com/pylangacq/pylangacq.git
    $ cd pylangacq
    $ python setup.py install

Use
---

The `chat` submodule has a `Reader` class that reads in a `.cha` file. The following example assumes that a `.cha` file such as [`eve01.cha`](http://childes.psy.cmu.edu/browser/index.php?url=Eng-NA-MOR/Brown/Eve/eve01.cha) is in the current directory.

```python
>>> from pylangacq.chat import Reader
>>> from pprint import pprint
>>> corpus = Reader('eve01.cha')
>>>
>>> # The metadata from the @ lines of eve01.cha
... # can be accessed by various methods:
... #     metadata(), participants(), participant_codes(), languages(),
... #     date(), age()
...
>>> # The metadata @ lines in eve01.cha (excluding Time Duration and Tape Location)
... # are as follows:
...
>>> # @UTF8
... # @Begin
... # @Languages:	eng
... # @Participants:	CHI Eve Target_Child , MOT Sue Mother , COL Colin Investigator , RIC Richard Investigator
... # @ID:	eng|Brown|CHI|1;6.|female|||Target_Child|||
... # @ID:	eng|Brown|MOT|||||Mother|||
... # @ID:	eng|Brown|COL|||||Investigator|||
... # @ID:	eng|Brown|RIC|||||Investigator|||
... # @Date:	15-OCT-1962
... # @End
...
>>> pprint(corpus.metadata())
{'Date': '17-OCT-1962',
 'Languages': 'eng',
 'Participants': {'CHI': {'SES': '',
                          'age': '1;6.',
                          'corpus': 'Brown',
                          'custom': '',
                          'education': '',
                          'group': '',
                          'language': 'eng',
                          'role': 'Target_Child',
                          'sex': 'female',
                          'speaker_label': 'Eve Target_Child'},
                  'COL': {'SES': '',
                          'age': '',
                          'corpus': 'Brown',
                          'custom': '',
                          'education': '',
                          'group': '',
                          'language': 'eng',
                          'role': 'Investigator',
                          'sex': '',
                          'speaker_label': 'Colin Investigator'},
                  'MOT': {'SES': '',
                          'age': '',
                          'corpus': 'Brown',
                          'custom': '',
                          'education': '',
                          'group': '',
                          'language': 'eng',
                          'role': 'Mother',
                          'sex': '',
                          'speaker_label': 'Sue Mother'},
                  'RIC': {'SES': '',
                          'age': '',
                          'corpus': 'Brown',
                          'custom': '',
                          'education': '',
                          'group': '',
                          'language': 'eng',
                          'role': 'Investigator',
                          'sex': '',
                          'speaker_label': 'Richard Investigator'}},
 'Tape Location': '850',
 'Time Duration': '11:30-12:00',
 'UTF8': ''}
>>>
>>> pprint(corpus.participants())
{'CHI': {'SES': '',
         'age': '1;6.',
         'corpus': 'Brown',
         'custom': '',
         'education': '',
         'group': '',
         'language': 'eng',
         'role': 'Target_Child',
         'sex': 'female',
         'speaker_label': 'Eve Target_Child'},
 'COL': {'SES': '',
         'age': '',
         'corpus': 'Brown',
         'custom': '',
         'education': '',
         'group': '',
         'language': 'eng',
         'role': 'Investigator',
         'sex': '',
         'speaker_label': 'Colin Investigator'},
 'MOT': {'SES': '',
         'age': '',
         'corpus': 'Brown',
         'custom': '',
         'education': '',
         'group': '',
         'language': 'eng',
         'role': 'Mother',
         'sex': '',
         'speaker_label': 'Sue Mother'},
 'RIC': {'SES': '',
         'age': '',
         'corpus': 'Brown',
         'custom': '',
         'education': '',
         'group': '',
         'language': 'eng',
         'role': 'Investigator',
         'sex': '',
         'speaker_label': 'Richard Investigator'}}
>>>
>>> corpus.participant_codes()
{'CHI', 'RIC', 'COL', 'MOT'}
>>>
>>> corpus.languages()
{'eng'}
>>>
>>> corpus.date()
(1962, 10, 17)  # a 3-tuple of int for 17-OCT-1962
>>>
>>> corpus.age()
(1, 6, 0)  # a 3-tuple of int for 1 year and 6 months old; default is for CHI
>>>
>>> corpus.age(speaker='MOT')
(0, 0, 0)  # participants other than CHI often don't have the age info
```

Many, many more functionalities are coming.


Changlog
--------

See [changlog](ChangeLog.md)


Author
------

PyLangAcq is maintained by [Jackson Lee](http://jacksonllee.com/).

