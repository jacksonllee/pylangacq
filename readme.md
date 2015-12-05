PyLangAcq: Language acquisition research in Python
==================================================

What is this
------------

This library is current under active development. It is envisioned to be particularly useful for the computational modeling of language acquisition.

Currently, the focus is to develop capabilities to interface with `.cha` transcription files in the CHAT format, widely used by the [CHILDES](http://childes.psy.cmu.edu/) database.

As the CHAT format is used for conversation transcriptions more generally, researchers whose work is concerned with transcribed speech, conversation analysis, and other related areas will also benefit from this library.

Download
--------

PyLangAcq is currently available through GitHub:

    $ git clone https://github.com/pylangacq/pylangacq.git
    $ cd pylangacq
    $ python3 setup.py install

Use
---

The `chat` submodule has a `Reader` class that reads in a `.cha` file. The following example assumes that a `.cha` file such as `eve01.cha` is in the current directory.

```python
from pylangacq.chat import Reader
data = Reader('eve01.cha')
data.age()
# outputs the tuple (1, 6, 0), for 1 year, 6 months, and 0 days
# as the age of the target child (Eve) for eve01.cha
```

Many, many more functionalities are coming.


Author
------

PyLangAcq is maintained by [Jackson Lee](http://jacksonllee.com/).

