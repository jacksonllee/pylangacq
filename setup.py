import os
import setuptools


_VERSION = "0.12.0"

_THIS_DIR = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(_THIS_DIR, "README.md")) as f:
    _LONG_DESCRIPTION = f.read().strip()


def main():
    setuptools.setup(
        name="pylangacq",
        version=_VERSION,
        description="PyLangAcq: Language Acquisition Research in Python",
        long_description=_LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        url="http://pylangacq.org/",
        author="Jackson L. Lee",
        author_email="jacksonlunlee@gmail.com",
        license="MIT License",
        packages=setuptools.find_packages(),
        python_requires=">=3.6",
        setup_requires="setuptools>=39",
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
        data_files=[(".", ["LICENSE.txt", "CHANGELOG.md"])],
    )


if __name__ == "__main__":
    main()
