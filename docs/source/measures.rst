.. _measures:

Developmental Measures
======================

Several developmental measures are defined as :class:`~pylangacq.chat.Reader` methods:

.. currentmodule:: pylangacq.chat.Reader

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
    [2.316421895861148,
     2.5163934426229506,
     2.8063241106719365,
     2.611864406779661,
     2.8854314002828856,
     3.195571955719557,
     3.1818181818181817,
     3.4171011470281543,
     3.840690978886756,
     3.822669104204753,
     3.883668903803132,
     4.165123456790123,
     4.269565217391304,
     3.976890756302521,
     4.457182320441989,
     4.422776911076443,
     4.495575221238938,
     4.292035398230088,
     4.3813169984686064,
     3.320964749536178]
