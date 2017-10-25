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
    eve01.cha 0.18005540166204986
    eve02.cha 0.24435590969455512
    eve03.cha 0.29637526652452023
    eve04.cha 0.2139917695473251
    eve05.cha 0.22727272727272727
    eve06.cha 0.22148209825145712
    eve07.cha 0.2356115107913669
    eve08.cha 0.16767241379310344
    eve09.cha 0.18788713007570543
    eve10.cha 0.18881578947368421
    eve11.cha 0.20516962843295639
    eve12.cha 0.16790490341753342
    eve13.cha 0.2024623803009576
    eve14.cha 0.22341184867951464
    eve15.cha 0.1723430447271235
    eve16.cha 0.17647058823529413
    eve17.cha 0.17472240365774003
    eve18.cha 0.17892253244199763
    eve19.cha 0.18863530507685142
    eve20.cha 0.24420529801324503

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
    eve01.cha 2.267022696929239
    eve02.cha 2.4487704918032787
    eve03.cha 2.7628458498023716
    eve04.cha 2.5762711864406778
    eve05.cha 2.8585572842998586
    eve06.cha 3.177121771217712
    eve07.cha 3.1231060606060606
    eve08.cha 3.3743482794577684
    eve09.cha 3.817658349328215
    eve10.cha 3.7915904936014626
    eve11.cha 3.865771812080537
    eve12.cha 4.157407407407407
    eve13.cha 4.239130434782608
    eve14.cha 3.9600840336134455
    eve15.cha 4.4502762430939224
    eve16.cha 4.4243369734789395
    eve17.cha 4.46570796460177
    eve18.cha 4.288242730720607
    eve19.cha 4.347626339969372
    eve20.cha 3.163265306122449

For ``MLUw()``:

.. code-block:: python

    >>> for filename, mluw in sorted(eve.MLUw().items()):
    ...     print(os.path.basename(filename), mluw)
    ...
    eve01.cha 1.4459279038718291
    eve02.cha 1.5430327868852458
    eve03.cha 1.8537549407114624
    eve04.cha 1.647457627118644
    eve05.cha 1.8981612446958982
    eve06.cha 2.215867158671587
    eve07.cha 2.106060606060606
    eve08.cha 2.4191866527632953
    eve09.cha 2.7888675623800383
    eve10.cha 2.7787934186471666
    eve11.cha 2.7695749440715884
    eve12.cha 3.115740740740741
    eve13.cha 3.1782608695652175
    eve14.cha 2.94327731092437
    eve15.cha 3.366022099447514
    eve16.cha 3.3681747269890794
    eve17.cha 3.3871681415929205
    eve18.cha 3.2149178255372948
    eve19.cha 3.2879019908116387
    eve20.cha 2.241187384044527

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
