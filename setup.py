import os
import re
import setuptools


_VERSION = "0.13.0"

_THIS_DIR = os.path.dirname(os.path.realpath(__file__))


def _get_long_description():
    with open(os.path.join(_THIS_DIR, "README.rst"), encoding="utf8") as f:
        readme = f.read().strip()
    # PyPI / twine doesn't accept the `raw` directive in reStructuredText.
    long_description = re.sub(
        r"\.\. start-raw-directive[\s\S]+?\.\. end-raw-directive", "", readme
    )
    return long_description


def main():
    setuptools.setup(
        name="pylangacq",
        version=_VERSION,
        description="PyLangAcq: Language Acquisition Research in Python",
        long_description=_get_long_description(),
        long_description_content_type="text/x-rst",
        url="https://pylangacq.org/",
        project_urls={
            "Bug Tracker": "https://github.com/jacksonllee/pylangacq/issues",
            "Source Code": "https://github.com/jacksonllee/pylangacq",
        },
        download_url="https://pypi.org/project/pylangacq/#files",
        author="Jackson L. Lee",
        author_email="jacksonlunlee@gmail.com",
        license="MIT License",
        packages=setuptools.find_packages(),
        python_requires=">=3.6",
        setup_requires="setuptools>=39",
        install_requires=[
            "dataclasses ; python_version < '3.7'",
            "python-dateutil>=2.0.0,<=3.0.0",
            "requests>=2.18.0,<=3.0.0",
        ],
        keywords=[
            "computational linguistics",
            "natural language processing",
            "NLP",
            "linguistics",
            "corpora",
            "speech",
            "language",
            "CHILDES",
            "CHAT",
            "transcription",
            "acquisition",
            "development",
            "learning",
        ],
        package_data={"pylangacq": ["tests/test_data/*"]},
        zip_safe=False,
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Intended Audience :: Information Technology",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Scientific/Engineering :: Human Machine Interfaces",
            "Topic :: Scientific/Engineering :: Information Analysis",
            "Topic :: Text Processing",
            "Topic :: Text Processing :: Filters",
            "Topic :: Text Processing :: General",
            "Topic :: Text Processing :: Indexing",
            "Topic :: Text Processing :: Linguistic",
        ],
        data_files=[(".", ["README.rst", "LICENSE.txt", "CHANGELOG.md"])],
    )


if __name__ == "__main__":
    main()
