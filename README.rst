PyLangAcq: Language Acquisition Research in Python
==================================================

Full documentation: https://pylangacq.org

|

.. image:: https://badge.fury.io/py/pylangacq.svg
   :target: https://pypi.python.org/pypi/pylangacq
   :alt: PyPI version

.. image:: https://img.shields.io/conda/vn/conda-forge/pylangacq.svg
   :target: https://anaconda.org/conda-forge/pylangacq
   :alt: Conda version

.. image:: https://img.shields.io/pypi/pyversions/pylangacq.svg
   :target: https://pypi.python.org/pypi/pylangacq
   :alt: Supported Python versions

|

.. start-sphinx-website-index-page

PyLangAcq is a Python library for language acquisition research.

- Reading and writing the CHAT data format used by TalkBank and CHILDES datasets
- Intuitive Python data structures for flexible data access and manipulation
- Standard developmental measures readily available: Mean length of utterance (MLU),
  type-token ratio (TTR), and Index of Productive Syntax (IPSyn)
- Direct support and powerful extensions possible for CHAT-formatted conversational datasets
  more generally

Since v0.20.0 (February 2026), PyLangAcq depends on
`Rustling <https://docs.rustling.io>`_,
a library for efficiently handling CHAT data and other computational linguistics tasks.


.. _download_install:

Download and Install
--------------------

Using pip::

   pip install --upgrade pylangacq

Using conda::

   conda install -c conda-forge pylangacq

Ready for more?
Check out the `Quickstart <https://pylangacq.org/quickstart.html>`_ page.

Links
-----

* Documentation: https://pylangacq.org
* Source code: https://github.com/jacksonllee/pylangacq
* Author: `Jackson L. Lee <https://jacksonllee.com>`_

How to Cite
-----------

Lee, Jackson L., Ross Burkholder, Gallagher B. Flinn, and Emily R. Coppess. 2016.
`Working with CHAT transcripts in Python <https://jacksonllee.com/papers/lee-etal-2016-pylangacq.pdf>`_.
Technical report `TR-2016-02 <https://newtraell.cs.uchicago.edu/research/publications/techreports/TR-2016-02>`_,
Department of Computer Science, University of Chicago.

.. code-block:: latex

    @TechReport{lee-et-al-pylangacq:2016,
       Title       = {Working with CHAT transcripts in Python},
       Author      = {Lee, Jackson L. and Burkholder, Ross and Flinn, Gallagher B. and Coppess, Emily R.},
       Institution = {Department of Computer Science, University of Chicago},
       Year        = {2016},
       Number      = {TR-2016-02},
    }

License
-------

MIT License

.. end-sphinx-website-index-page
