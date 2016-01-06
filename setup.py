from setuptools import (setup, find_packages)

setup(name="pylangacq",
    version="0.7",
    description="PyLangAcq",

    long_description="""
PyLangAcq: Language Acquisition Research in Python
""",

    url="http://pylangacq.github.io/",
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
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
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
