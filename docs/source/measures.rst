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
     2.618803418803419,
     2.8852691218130313,
     3.203358208955224,
     3.179732313575526,
     3.4171011470281543,
     3.8439306358381504,
     3.822669104204753,
     3.8814317673378076,
     4.177847113884555,
     4.2631578947368425,
     3.9936974789915967,
     4.457182320441989,
     4.416536661466458,
     4.501661129568106,
     4.288242730720607,
     4.3813169984686064,
     3.3172541743970316]
