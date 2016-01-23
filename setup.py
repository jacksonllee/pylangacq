from os import path
import sys
from setuptools import (setup, find_packages)

py_version = sys.version_info[:2]
if py_version < (3, 4):
    sys.exit('Error: PyLangAcq requires Python 3.4 or above.\n'
             'You are using Python {}.{}.'.format(*py_version))

version_filename = path.join(path.dirname(__file__), 'pylangacq', 'VERSION')
with open(version_filename) as f:
    package_version = f.read().strip()

setup(name="pylangacq",
    version=package_version,
    description="PyLangAcq",
    long_description="PyLangAcq: Language Acquisition Research in Python",
    url="http://pylangacq.org/",
    author="Jackson Lee",
    author_email="jsllee.phon@gmail.com",
    license="Apache License, Version 2.0",
    packages=find_packages(),
    keywords=['computational linguistics', 'natural language processing',
              'NLP', 'linguistics', 'corpora', 'speech',
              'language', 'CHILDES', 'CHAT', 'transcription',
              'acquisition', 'development', 'learning'],

    install_requires=['networkx'],

    zip_safe=False,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
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

    package_data = {'pylangacq': ['VERSION']}
)
