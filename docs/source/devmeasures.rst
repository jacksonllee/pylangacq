.. _devmeasures:

Developmental measures
======================

Several language developmental measures are implemented in PyLangAcq:

======================  ==============================================
Method                  Measure
======================  ==============================================
:ref:`TTR() <ttr>`      Type-token Ratio
:ref:`MLUm() <mlu>`     Mean Length of Utterance in morphemes
:ref:`MLUw() <mlu>`     Mean Length of Utterance in words
:ref:`MLU() <mlu>`      (same as ``MLUm()``; included for convenience)
:ref:`IPSyn() <ipsyn>`  Index of Productive Syntax
======================  ==============================================

All these methods have the optional parameter ``participant`` which defaults
to ``'CHI'``.

All these methods take a CHAT transcript file as a working unit and compute
an output number for the relevant measure for that file. They can all be
applied to a ``Reader`` instance, and
the return object is dict(filename: measure for that file).

In the following examples, we use Eve's data from CHILDES Brown:

.. code-block:: python

    >>> import os
    >>> import pylangacq as pla
    >>> eve = pla.read_chat('Brown/Eve/*.cha')

.. _ttr:

Type-token Ratio (TTR)
----------------------

The type-token ratio is the total word type count divided by the total word
token count in a given CHAT file:

.. code-block:: python

    >>> for filename, ttr in sorted(eve.TTR().items()):
    ...     print(os.path.basename(filename), ttr)
    ...
    010600a.cha 0.17543859649122806
    010600b.cha 0.23853211009174313
    010700a.cha 0.29324894514767935
    010700b.cha 0.20525783619817997
    010800.cha 0.2223869532987398
    010900a.cha 0.21445978878960195
    010900b.cha 0.2288512911843277
    010900c.cha 0.16100254885301615
    011000a.cha 0.18311776718856365
    011000b.cha 0.18319107025607353
    011100a.cha 0.20016142050040356
    011100b.cha 0.1628021706956093
    020000a.cha 0.19687712152070605
    020000b.cha 0.21627408993576017
    020100a.cha 0.1642156862745098
    020100b.cha 0.16967175219602404
    020200a.cha 0.17028867985728185
    020200b.cha 0.1762858264625049
    020300a.cha 0.1863932898415657
    020300b.cha 0.23655913978494625

.. _mlu:

Mean Length of Utterance (MLU)
------------------------------

The mean length of utterance (MLU) comes in two flavors: in morphemes and in
words. Both ``MLUm()`` and ``MLUw()`` are available;
for convenience, ``MLU()`` is also implemented and works exactly like
``MLUm()``.

For ``MLUm()``:

.. code-block:: python

    >>> for filename, mlum in sorted(eve.MLUm().items()):
    ...     print(os.path.basename(filename), mlum)
    ...
    010600a.cha 2.267022696929239
    010600b.cha 2.4508196721311477
    010700a.cha 2.7628458498023716
    010700b.cha 2.571186440677966
    010800.cha 2.8528995756718527
    010900a.cha 3.1734317343173433
    010900b.cha 3.1268939393939394
    010900c.cha 3.380604796663191
    011000a.cha 3.8214971209213053
    011000b.cha 3.8062157221206583
    011100a.cha 3.87248322147651
    011100b.cha 4.157407407407407
    020000a.cha 4.247826086956522
    020000b.cha 3.9684873949579833
    020100a.cha 4.448895027624309
    020100b.cha 4.416536661466458
    020200a.cha 4.476769911504425
    020200b.cha 4.286978508217446
    020300a.cha 4.346094946401225
    020300b.cha 3.165120593692022

For ``MLUw()``:

.. code-block:: python

    >>> for filename, mluw in sorted(eve.MLUw().items()):
    ...     print(os.path.basename(filename), mluw)
    ...
    010600a.cha 1.4459279038718291
    010600b.cha 1.5635245901639345
    010700a.cha 1.8735177865612649
    010700b.cha 1.676271186440678
    010800.cha 1.908062234794908
    010900a.cha 2.2712177121771218
    010900b.cha 2.1268939393939394
    010900c.cha 2.454640250260688
    011000a.cha 2.81957773512476
    011000b.cha 2.7842778793418645
    011100a.cha 2.771812080536913
    011100b.cha 3.128086419753086
    020000a.cha 3.2021739130434783
    020000b.cha 2.94327731092437
    020100a.cha 3.3812154696132595
    020100b.cha 3.374414976599064
    020200a.cha 3.4103982300884956
    020200b.cha 3.2199747155499368
    020300a.cha 3.286370597243492
    020300b.cha 2.2430426716141003

.. _ipsyn:

Index of Productive Syntax (IPSyn)
----------------------------------

The Index of Productive Syntax (IPSyn; Scarborough 1990) is a measure of
language development encompassing 56 morphological and syntactic/semantic
test items.
Relying on ``%mor`` and ``%gra`` tiers,
the IPSyn computation takes the first 100 child utterances in a
given CHAT transcript and scores each of the 56 items for points of
0 (for no occurrences),
1 (for one occurrence), or 2 (for two or more occurrences). The overall IPSyn
score sums all these 56 sub-scores, giving a number from 0 to 112 inclusive:

.. code-block:: python

    >>> for filename, ipsyn in sorted(eve.IPSyn().items()):
    ...     print(os.path.basename(filename), ipsyn)
    ...
    010600a.cha 29
    010600b.cha 45
    010700a.cha 36
    010700b.cha 36
    010800.cha 44
    010900a.cha 44
    010900b.cha 39
    010900c.cha 42
    011000a.cha 47
    011000b.cha 55
    011100a.cha 55
    011100b.cha 66
    020000a.cha 62
    020000b.cha 69
    020100a.cha 77
    020100b.cha 75
    020200a.cha 70
    020200b.cha 70
    020300a.cha 87
    020300b.cha 66
