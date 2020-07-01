# PyLangAcq

[![CircleCI](https://circleci.com/gh/jacksonllee/pylangacq/tree/master.svg?style=svg)](https://circleci.com/gh/jacksonllee/pylangacq/tree/master)
[![PyPI version](https://badge.fury.io/py/pylangacq.svg)](https://pypi.org/project/pylangacq)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pylangacq.svg)](https://pypi.org/project/pylangacq)

PyLangAcq is a Python library for language acquisition research.
It allows flexible handling of the CHILDES data.

Full documentation: http://pylangacq.org/

## Features

- Comprehensive capabilities of handling CHAT transcripts as used in CHILDES
- Intuitive data structures for flexible data access and all sorts of modeling work
- Standard developmental measures such as TTR, MLU, and IPSyn readily available
- More benefits from Python: fast coding, numerous libraries
  for computational modeling and machine learning
- Powerful extensions for research with conversational data in general

## Download and install

PyLangAcq is available via `pip`:

```bash
pip install -U pylangacq
```

PyLangAcq works with Python 3.6 or above.

## Development

The source code of PyLangAcq is hosted on GitHub at
https://github.com/jacksonllee/pylangacq,
where development also happens.

For the latest changes not yet released through `pip` or working on the codebase
yourself, you may obtain the latest source code through GitHub and `git`:

1. Create a fork of the `pylangacq` repo under your GitHub account.
2. Locally, make sure you are in some sort of a virtual environment
   (venv, virtualenv, conda, etc).
3. Download and install the library in the "editable" mode
   together with the core and dev dependencies within the virtual environment:

    ```bash
    git clone https://github.com/<your-github-username>/pylangacq.git
    cd pylangacq
    pip install --upgrade pip setuptools
    pip install -r dev-requirements.txt
    pip install -e .
    ```

We keep track of notable changes in
[CHANGELOG.md](https://github.com/jacksonllee/pylangacq/blob/master/CHANGELOG.md).

## Contribution

For questions, bug reports, and feature requests,
please [file an issue](https://github.com/jacksonllee/pylangacq/issues).

If you would like to contribute to the `pylangacq` codebase,
please see
[CONTRIBUTING.md](https://github.com/jacksonllee/pylangacq/blob/master/CONTRIBUTING.md).

## How to Cite

PyLangAcq is maintained by [Jackson Lee](http://jacksonllee.com/).
If you use PyLangAcq in your research, please cite the following:

Lee, Jackson L., Ross Burkholder, Gallagher B. Flinn, and Emily R. Coppess. 2016.
[Working with CHAT transcripts in Python](http://jacksonllee.com/papers/lee-etal-2016-pylangacq.pdf).
Technical report [TR-2016-02](http://www.cs.uchicago.edu/research/publications/techreports/TR-2016-02),
Department of Computer Science, University of Chicago.

```bibtex
@TechReport{lee-et-al-pylangacq:2016,
   Title       = {Working with CHAT transcripts in Python},
   Author      = {Lee, Jackson L. and Burkholder, Ross and Flinn, Gallagher B. and Coppess, Emily R.},
   Institution = {Department of Computer Science, University of Chicago},
   Year        = {2016},
   Number      = {TR-2016-02},
}
```

## License

The MIT License; please see [LICENSE.txt](https://github.com/jacksonllee/pylangacq/blob/master/LICENSE.txt).
The test data files included
have a [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/)
license instead; please also see
[`pylangacq/tests/test_data/README.md`](https://github.com/jacksonllee/pylangacq/blob/master/pylangacq/tests/test_data/README.md).
