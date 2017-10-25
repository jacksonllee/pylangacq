from os import path
from setuptools import (setup, find_packages)


THIS_DIR = path.dirname(__file__)

with open(path.join(THIS_DIR, 'pylangacq', 'VERSION')) as f:
    package_version = f.read().strip()

with open(path.join(THIS_DIR, 'README.rst')) as f:
    long_description = f.read()

with open(path.join(THIS_DIR, 'requirements.txt')) as f:
    requirements = [x.strip() for x in f.readlines()]


def main():
    setup(
        name="pylangacq",
        version=package_version,
        description="PyLangAcq: Language Acquisition Research in Python",
        long_description=long_description,
        url="http://pylangacq.org/",
        author="Jackson Lee",
        author_email="jacksonlunlee@gmail.com",
        license="MIT License",
        packages=find_packages(),
        keywords=['computational linguistics', 'natural language processing',
                  'NLP', 'linguistics', 'corpora', 'speech',
                  'language', 'CHILDES', 'CHAT', 'transcription',
                  'acquisition', 'development', 'learning'],

        package_data={'pylangacq': ['VERSION']},

        install_requires=requirements,

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


if __name__ == "__main__":
    main()
