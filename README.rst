PyLangAcq: Language Acquisition Research in Python
==================================================

Full documentation: https://pylangacq.org

|

.. image:: https://badge.fury.io/py/pylangacq.svg
   :target: https://pypi.python.org/pypi/pylangacq
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pylangacq.svg
   :target: https://pypi.python.org/pypi/pylangacq
   :alt: Supported Python versions

.. image:: https://circleci.com/gh/jacksonllee/pylangacq/tree/main.svg?style=svg
   :target: https://circleci.com/gh/jacksonllee/pylangacq/tree/main
   :alt: Build

|

.. start-sphinx-website-index-page

PyLangAcq is a Python library for language acquisition research.

- Comprehensive capabilities of handling CHAT transcripts as used in CHILDES
- Intuitive Python data structures for flexible data access and manipulation for modeling work
- Standard developmental measures readily available: Mean length of utterance (MLU),
  type-token ratio (TTR), and index of productive syntax (IPSyn)
- More benefits from Python: Fast prototyping, numerous libraries
  for computational modeling and machine learning
- Powerful extensions for research with conversational data in general

.. _download_install:

Download and Install
--------------------

To download and install the most recent version::

    $ pip install --upgrade pylangacq

To test your installation in the Python interpreter:

.. code-block:: python

    >>> import pylangacq
    >>> pylangacq.__version__  # show version number

Ready for more?
Check out the `Quickstart <https://pylangacq.org/quickstart.html>`_ page.

Links
-----

* Source code: https://github.com/jacksonllee/pylangacq
* Bug tracker, feature requests: https://github.com/jacksonllee/pylangacq/issues
* Email: Please contact `Jackson Lee <https://jacksonllee.com>`_.
* Social media: `Twitter <https://twitter.com/pylangacq>`_

How to Cite
-----------

PyLangAcq is authored and maintained by `Jackson L. Lee <https://jacksonllee.com>`_.

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

MIT License. Please see ``LICENSE.txt`` in the GitHub source code for details.

The test data files included come from CHILDES,
and have a `CC BY-NC-SA 3.0 <https://creativecommons.org/licenses/by-nc-sa/3.0/>`_
license instead; please also see
``pylangacq/tests/test_data/README.md`` in the GitHub source code for details.

.. end-sphinx-website-index-page

Changelog
---------

Please see ``CHANGELOG.md``.

Setting up a Development Environment
------------------------------------

The latest code under development is available on Github at
`jacksonllee/pylangacq <https://github.com/jacksonllee/pylangacq>`_.
To obtain this version for experimental features or for development:

.. code-block:: bash

   $ git clone https://github.com/jacksonllee/pylangacq.git
   $ cd pylangacq
   $ pip install -r dev-requirements.txt
   $ pip install -e .

To run tests and styling checks:

.. code-block:: bash

   $ pytest -vv --doctest-modules --cov=pylangacq pylangacq docs
   $ flake8 pylangacq
   $ black --check pylangacq

To build the documentation website files:

.. code-block:: bash

    $ python build_docs.py
