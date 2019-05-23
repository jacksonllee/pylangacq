import os
import sys
import warnings

from setuptools import setup, find_packages


_PACKAGE_NAME = 'pylangacq'
_PYTHON_VERSION = sys.version_info[:3]
_THIS_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(_THIS_DIR, _PACKAGE_NAME, '_version.py')) as f:
    # get __version__
    exec(f.read())

with open(os.path.join(_THIS_DIR, 'README.rst')) as f:
    _LONG_DESCRIPTION = f.read().strip()


def main():
    if _PYTHON_VERSION < (3, 5):
        warnings.warn(
            'You are currently on Python {py_version}. '
            'Python < 3.5 is deprecated and not supported '
            'since pylangacq v0.11.0. '.format(
                py_version='.'.join(_PYTHON_VERSION)
            ),
            DeprecationWarning
        )

    setup(
        name=_PACKAGE_NAME,
        version=__version__,  # noqa: F821
        description='PyLangAcq: Language Acquisition Research in Python',
        long_description=_LONG_DESCRIPTION,
        url='http://pylangacq.org/',
        author='Jackson Lee',
        author_email='jacksonlunlee@gmail.com',
        license='MIT License',
        packages=find_packages(),
        keywords=['computational linguistics', 'natural language processing',
                  'NLP', 'linguistics', 'corpora', 'speech',
                  'language', 'CHILDES', 'CHAT', 'transcription',
                  'acquisition', 'development', 'learning'],

        package_data={'pylangacq': ['tests/test_data/*']},

        zip_safe=False,

        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Information Technology',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Scientific/Engineering :: Human Machine Interfaces',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Text Processing',
            'Topic :: Text Processing :: Filters',
            'Topic :: Text Processing :: General',
            'Topic :: Text Processing :: Indexing',
            'Topic :: Text Processing :: Linguistic'
        ],
    )


if __name__ == '__main__':
    main()
