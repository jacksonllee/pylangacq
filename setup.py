import os
import re
import setuptools


_THIS_DIR = os.path.dirname(os.path.realpath(__file__))


def _get_long_description():
    with open(os.path.join(_THIS_DIR, "README.rst"), encoding="utf8") as f:
        readme = f.read().strip()
    # PyPI / twine doesn't accept the `raw` directive in reStructuredText.
    long_description = re.sub(
        r"\.\. start-raw-directive[\s\S]+?\.\. end-raw-directive", "", readme
    )
    return long_description


def _get_version():
    version = open(os.path.join(_THIS_DIR, "pylangacq", "_version.py"), "r").read()
    regex = r"(?P<major>\d+)(.(?P<minor>\d+))?(.(?P<patch>\d+))?"
    match = re.search(regex, version)
    if not match:
        raise RuntimeError("Unable to find version string.")
    return f'{match.group("major")}.{match.group("minor")}.{match.group("patch")}'


def main():
    setuptools.setup(
        name="pylangacq",
        version=_get_version(),
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
        python_requires=">=3.7",
        setup_requires="setuptools>=39",
        install_requires=[
            "python-dateutil>=2.0.0,<=3.0.0",
            "requests>=2.18.0,<=3.0.0",
            "tabulate[widechars]>=0.8.9,<=0.9.0",
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
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
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
