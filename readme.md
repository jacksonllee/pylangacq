PyLangAcq: Language acquisition research in Python
==================================================

What is this
------------

PyLangAcq is a Python library for the computational modeling of language acquisition. The library is under active development. The current version is 0.7.

Currently, the focus is to develop capabilities to interface with `.cha` transcription files in the CHAT format, widely used by the [CHILDES](http://childes.psy.cmu.edu/) database.

As the CHAT format is used for conversation transcriptions more generally, researchers whose work is concerned with transcribed speech, conversation analysis, and other related areas will also benefit from this library.

Download and install
--------------------

PyLangAcq is currently available through GitHub:

    $ git clone https://github.com/pylangacq/pylangacq.git
    $ cd pylangacq
    $ python setup.py install

The command `python` is meant to be generic for whichever Python interpreter of your choice is. PyLangAcq is compatible with both Python 2 and 3.

Use
---

The `chat` submodule has two classes for reading `.cha` files:

- `SingleReader` for reading a single `.cha` file
- `Reader` for multiple `.cha` files

For `SingleReader`, the following example assumes that a `.cha` file such as [`eve01.cha`](http://childes.psy.cmu.edu/browser/index.php?url=Eng-NA-MOR/Brown/Eve/eve01.cha) is in the current directory.

```python
>>> from pylangacq.chat import SingleReader
>>> from pprint import pprint
>>> corpus = SingleReader('eve01.cha')
>>>
>>> # The metadata from the headers @ lines of eve01.cha
... # can be accessed by various methods:
... #     headers(), participants(), participant_codes(), languages(),
... #     date(), age()
...
>>> # The headers in eve01.cha (excluding Time Duration and Tape Location)
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
>>> corpus.number_of_utterances()
1588  # number of transcription lines starting with '*', for *CHI, *MOT, etc.
>>>
>>> pprint(corpus.headers)
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
                          'participant_label': 'Eve Target_Child'},
                  'COL': {'SES': '',
                          'age': '',
                          'corpus': 'Brown',
                          'custom': '',
                          'education': '',
                          'group': '',
                          'language': 'eng',
                          'role': 'Investigator',
                          'sex': '',
                          'participant_label': 'Colin Investigator'},
                  'MOT': {'SES': '',
                          'age': '',
                          'corpus': 'Brown',
                          'custom': '',
                          'education': '',
                          'group': '',
                          'language': 'eng',
                          'role': 'Mother',
                          'sex': '',
                          'participant_label': 'Sue Mother'},
                  'RIC': {'SES': '',
                          'age': '',
                          'corpus': 'Brown',
                          'custom': '',
                          'education': '',
                          'group': '',
                          'language': 'eng',
                          'role': 'Investigator',
                          'sex': '',
                          'participant_label': 'Richard Investigator'}},
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
         'participant_label': 'Eve Target_Child'},
 'COL': {'SES': '',
         'age': '',
         'corpus': 'Brown',
         'custom': '',
         'education': '',
         'group': '',
         'language': 'eng',
         'role': 'Investigator',
         'sex': '',
         'participant_label': 'Colin Investigator'},
 'MOT': {'SES': '',
         'age': '',
         'corpus': 'Brown',
         'custom': '',
         'education': '',
         'group': '',
         'language': 'eng',
         'role': 'Mother',
         'sex': '',
         'participant_label': 'Sue Mother'},
 'RIC': {'SES': '',
         'age': '',
         'corpus': 'Brown',
         'custom': '',
         'education': '',
         'group': '',
         'language': 'eng',
         'role': 'Investigator',
         'sex': '',
         'participant_label': 'Richard Investigator'}}
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
>>> corpus.age(participant='MOT')
(0, 0, 0)  # participants other than CHI often don't have the age info
>>>
>>> # Extract the first 10 utterances, with CHAT annotations removed (clean=True, the default)
...
>>>
>>> for i, (participant, utterance) in enumerate(corpus.utterances(clean=True)):
...     if i >= 10:
...         break
...     print('{}: {}'.format(participant, utterance))
...
CHI: more cookie .
MOT: you 0v more cookies ?
MOT: how_about another graham+cracker ?
MOT: would that do just as_well ?
MOT: here .
MOT: here you go .
CHI: more cookie .
MOT: you have another cookie right on the table .
CHI: more juice ?
MOT: more juice ?
>>>
>>> # Extract the first 10 utterances by the target child
...
>>> for i, (participant, utterance) in enumerate(corpus.utterances(participant='CHI', clean=True)):
...     if i >= 10:
...         break
...     print('{}: {}'.format(participant, utterance))
...
CHI: more cookie .
CHI: more cookie .
CHI: more juice ?
CHI: Fraser .
CHI: Fraser .
CHI: Fraser .
CHI: Fraser .
CHI: yeah .
CHI: (th)at ?
CHI: a fly .
```


The class `Reader` is available for reading multiple `.cha` files. `Reader` shares the same method names as `SingleReader`. Because `Reader` is the generalized reader for multiple input files built on top of `SingleReader`, the `Reader` methods have a more elaborate data structure, mostly returning a dict mapping a absolute-path filename to whatever the method is for with respect to the file concerned. Example (assuming the `.cha` files for Eve from CHILDES Brown are in the current directory):

```python
>>> import os
>>> from pylangacq.chat import Reader
>>> eve_corpus = Reader('eve*.cha')  # allows filename pattern matching with *
>>>
>>> eve_corpus.number_of_files()
20  # there are 20 files for Eve, from eve01.cha through eve20.cha
>>>
>>> eve_corpus.number_of_utterances()
26921  # total number of utterances for the Eve portion in Brown
>>>
>>> eve_ages = eve_corpus.age()  # a dict (key: abs-path filename, value: age as a 3-int tuple)
>>> eve_ages_sorted = sorted([(os.path.basename(fn), age) for fn, age in eve_ages.items()])
>>> for filename, age in eve_ages_sorted:
...     print(filename, age)
...
eve01.cha (1, 6, 0)
eve02.cha (1, 6, 0)
eve03.cha (1, 7, 0)
eve04.cha (1, 7, 0)
eve05.cha (1, 8, 0)
eve06.cha (1, 9, 0)
eve07.cha (1, 9, 0)
eve08.cha (1, 9, 0)
eve09.cha (1, 10, 0)
eve10.cha (1, 10, 0)
eve11.cha (1, 11, 0)
eve12.cha (1, 11, 0)
eve13.cha (2, 0, 0)
eve14.cha (2, 0, 0)
eve15.cha (2, 1, 0)
eve16.cha (2, 1, 0)
eve17.cha (2, 2, 0)
eve18.cha (2, 2, 0)
eve19.cha (2, 3, 0)
eve20.cha (2, 3, 0)
```



Many, many more functionalities are coming.


Syntax highlighting for CHAT transcripts
----------------------------------------

See the directory [`chat-syntax-highlighting`](chat-syntax-highlighting).


Changlog
--------

See [changlog](changelog.md)


License
-------

See [license](license.txt)


Author
------

PyLangAcq is maintained by [Jackson Lee](http://jacksonllee.com/).

