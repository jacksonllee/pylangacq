.. _measures:

Developmental Measures
======================

Some developmental measures are defined as :class:`~pylangacq.CHAT` methods:

.. currentmodule:: pylangacq.CHAT

.. autosummary::

    mlu
    mlum
    mluw
    ttr
    ipsyn


For the mean length of utterance in morphemes in Eve's data from Brown:

.. code-block:: python

    import pylangacq
    eve = pylangacq.read_chat("path/to/your/local/Brown.zip", filter_files="Eve")
    eve_chi = eve.filter(participants="CHI")
    eve_chi.mlum()
    # [1.43, 1.82, 2.15, 2.07, 2.16, 2.4, 2.43, 2.4, 2.86, 2.72, 2.69, 3.4, 3.5, 2.83, 3.54, 3.24, 3.61, 3.2, 3.8, 2.24]

The result is the MLU in morphemes for each of Eve's CHAT files in order.
As this is a list of floats, they can be readily piped into
other packages for making plots, for example:

.. code-block:: python

    import pylangacq

    # matplotlib and seaborn required for this code snippet
    import matplotlib.pyplot as plt
    import seaborn as sns

    brown = pylangacq.read_chat("path/to/your/local/Brown.zip")
    eve = brown.filter(files="Eve")
    eve_chi = eve.filter(participants="CHI")
    ages_in_months = [age.in_months() for age in eve_chi.ages()]

    plt.figure(figsize=(8, 5))
    sns.lineplot(
        x=ages_in_months,
        y=eve_chi.mlum(),
        errorbar=None,
    )

    plt.title("Mean Length of Utterance in Morphemes for Brown's Eve")
    plt.xlabel("Age in months")
    plt.ylabel("MLU (morphemes)")
    plt.xticks(ages_in_months)

    plt.savefig("brown_eve_mlum.png")
    plt.close()

.. image:: _static/brown_eve_mlum.png
   :alt: Mean Length of Utterance in Morphemes for Brown's Eve
