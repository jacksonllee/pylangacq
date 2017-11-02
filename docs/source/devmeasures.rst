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
    010900c.cha 0.16142735768903993
    011000a.cha 0.18231292517006803
    011000b.cha 0.18319107025607353
    011100a.cha 0.20016142050040356
    011100b.cha 0.1628021706956093
    020000a.cha 0.19687712152070605
    020000b.cha 0.21540656205420827
    020100a.cha 0.16483068135454917
    020100b.cha 0.16920239741816506
    020200a.cha 0.17017828200972449
    020200b.cha 0.17598748533437622
    020300a.cha 0.18472222222222223
    020300b.cha 0.23495465787304204

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
    010600a.cha 2.265687583444593
    010600b.cha 2.4487704918032787
    010700a.cha 2.7628458498023716
    010700b.cha 2.5728813559322035
    010800.cha 2.8528995756718527
    010900a.cha 3.1660516605166054
    010900b.cha 3.115530303030303
    010900c.cha 3.3733055265901983
    011000a.cha 3.817658349328215
    011000b.cha 3.7915904936014626
    011100a.cha 3.859060402684564
    011100b.cha 4.154320987654321
    020000a.cha 4.239130434782608
    020000b.cha 3.96218487394958
    020100a.cha 4.44475138121547
    020100b.cha 4.405616224648986
    020200a.cha 4.462389380530974
    020200b.cha 4.2768647281921615
    020300a.cha 4.339969372128637
    020300b.cha 3.1521335807050095

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
    011000a.cha 2.8214971209213053
    011000b.cha 2.7842778793418645
    011100a.cha 2.771812080536913
    011100b.cha 3.128086419753086
    020000a.cha 3.2021739130434783
    020000b.cha 2.9453781512605044
    020100a.cha 3.3853591160220993
    020100b.cha 3.3837753510140405
    020200a.cha 3.4126106194690267
    020200b.cha 3.232616940581542
    020300a.cha 3.30781010719755
    020300b.cha 2.250463821892393

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
    eve01.cha 29
    eve02.cha 44
    eve03.cha 36
    eve04.cha 39
    eve05.cha 43
    eve06.cha 42
    eve07.cha 39
    eve08.cha 45
    eve09.cha 50
    eve10.cha 62
    eve11.cha 59
    eve12.cha 69
    eve13.cha 64
    eve14.cha 76
    eve15.cha 80
    eve16.cha 77
    eve17.cha 75
    eve18.cha 71
    eve19.cha 88
    eve20.cha 65
