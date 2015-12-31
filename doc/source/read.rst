.. _read:

Reading data
============

Work in progress


``filenames()`` returns the set of absolute-path filenames in the data::

    >>> import os
    >>> for x in sorted(corpus.filenames()):
    ...     print(os.path.basename(x))  # show basenames only
    ...
    eve01.cha
    eve02.cha
    eve03.cha
    eve04.cha
    eve05.cha
    eve06.cha
    eve07.cha
    eve08.cha
    eve09.cha
    eve10.cha
    eve11.cha
    eve12.cha
    eve13.cha
    eve14.cha
    eve15.cha
    eve16.cha
    eve17.cha
    eve18.cha
    eve19.cha
    eve20.cha

