.. _measures:

Developmental Measures
======================

Several developmental measures are defined as :class:`~pylangacq.Reader` methods:

.. currentmodule:: pylangacq.Reader

.. autosummary::

    mlu
    mlum
    mluw
    ttr
    ipsyn


For the mean lengths of utterance (MLU) in Eve's data from Brown:

.. code-block:: python

    >>> import pylangacq
    >>> url = "https://childes.talkbank.org/data/Eng-NA/Brown.zip"
    >>> eve = pylangacq.read_chat(url, "Eve")
    >>> eve.mlu()
    [2.309041835357625,
     2.488372093023256,
     2.8063241106719365,
     2.6153846153846154,
     2.8866855524079322,
     3.208955223880597,
     3.179732313575526,
     3.4171011470281543,
     3.840077071290944,
     3.822669104204753,
     3.883668903803132,
     4.177847113884555,
     4.2631578947368425,
     3.976890756302521,
     4.457182320441989,
     4.422776911076443,
     4.498338870431894,
     4.292035398230088,
     4.3813169984686064,
     3.320964749536178]
