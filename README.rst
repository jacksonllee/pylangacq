PyLangAcq
=========

.. image:: https://badge.fury.io/py/pylangacq.svg
   :target: https://pypi.python.org/pypi/pylangacq
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pylangacq.svg
   :target: https://pypi.python.org/pypi/pylangacq
   :alt: Supported Python versions

.. image:: https://travis-ci.org/pylangacq/pylangacq.svg?branch=master
   :target: https://travis-ci.org/pylangacq/pylangacq
   :alt: Build


PyLangAcq is a Python library for language acquisition research.
It allows flexible handling of the CHILDES data.

Full documentation: http://pylangacq.org/


Features
--------

* Comprehensive capabilities of handling CHAT transcripts
  as used in CHILDES
* Intuitive data structures for flexible data access and all sorts of modeling work
* Standard developmental measures such as TTR, MLU, and IPSyn readily available
* More benefits from Python: fast coding, numerous libraries for computational
  modeling and machine learning
* Powerful extensions for research with conversational data in general


Download and install
--------------------

PyLangAcq is available via `pip`:

.. code-block:: bash

   $ pip install -U pylangacq

PyLangAcq works with Python 3.5+.
(Usage with Python 2.7 and 3.4 is deprecated starting from PyLangAcq v0.11.0.)


How to cite
-----------

PyLangAcq is maintained by `Jackson Lee <http://jacksonllee.com/>`_.
If you use PyLangAcq in your research,
please cite the following:

Lee, Jackson L., Ross Burkholder, Gallagher B. Flinn, and Emily R. Coppess. 2016.
`Working with CHAT transcripts in Python <http://jacksonllee.com/papers/lee-etal-2016-pylangacq.pdf>`_.
Technical report `TR-2016-02 <http://www.cs.uchicago.edu/research/publications/techreports/TR-2016-02>`_,
Department of Computer Science, University of Chicago.

.. code-block:: bash

   @TechReport{lee-et-al-pylangacq:2016,
      Title       = {Working with CHAT transcripts in Python},
      Author      = {Lee, Jackson L. and Burkholder, Ross and Flinn, Gallagher B. and Coppess, Emily R.},
      Institution = {Department of Computer Science, University of Chicago},
      Year        = {2016},
      Number      = {TR-2016-02},
   }


Change log
----------

See `CHANGELOG.md <CHANGELOG.md>`_.


License
-------

The MIT License. Please see `LICENSE.txt <LICENSE.txt>`_.
The test data files included have a `CC BY-NC-SA 3.0 <https://creativecommons.org/licenses/by-nc-sa/3.0/>`_
license instead -- please see ``pylangacq/tests/test_data/README.md``.
