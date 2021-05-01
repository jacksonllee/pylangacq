"""This script checks if PyLangAcq is compatible with TalkBank data.

Compatibility here means whether PyLangAcq can parse a TalkBank dataset by
aligning utterances with the mor/gra/etc tiers without raising errors.

This script is typically run by redirecting both stdout and stderr to
a log file that you can inspect. Update the PyLangAcq code and re-run this script
until no more errors are found. If you run this script from the repo root directory,
the terminal is something like this (using 'childes' as an example):

$ python scripts/check_talkbank_compatibility.py childes &> childes.log

"""

import argparse
import logging
import zipfile
from typing import Tuple

import requests

import pylangacq


_LOG = logging.getLogger(__name__)


_HAS_SUBDATASETS = {
    "childes": {
        "Celtic": {
            "Irish",
            "Welsh",
        },
        "Chinese": {
            "Cantonese",
            "Mandarin",
        },
        "Clinical-MOR": {
            "Ambrose",
            "Conti",
            "Feldman",
            "Nicholas",
            "Rondal",
        },
        "EastAsian": {
            "Thai",
            "Indonesian",
            "Korean",
        },
        "Other": {
            "Quechua",
            "Turkish",
            "Arabic",
            "Basque",
            "Estonian",
            "Farsi",
            "Greek",
            "Hebrew",
            "Hungarian",
            "Jamaican",
            "Nungon",
            "Sesotho",
            "Tamil",
        },
        "Romance": {
            "Catalan",
            "Italian",
            "Portuguese",
            "Romanian",
        },
        "Scandinavian": {
            "Danish",
            "Icelandic",
            "Norwegian",
            "Swedish",
        },
        "Slavic": {
            "Bulgarian",
            "Croatian",
            "Czech",
            "Polish",
            "Russian",
            "Serbian",
            "Slovenian",
        },
    },
}


def _check_compatibility(url: str, successes: int, failures: int) -> Tuple[int, int]:
    try:
        pylangacq.read_chat(url)
        successes += 1
    except zipfile.BadZipFile:
        _LOG.warning("Can't reach this dataset: %r", url)
        failures += 1
    except:  # noqa
        _LOG.exception("Can't parse %r -> %r -> %r", db, corpus, dataset)
        failures += 1
    return successes, failures


if __name__ == "__main__":
    logging.basicConfig(level="INFO")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("db", help="Specify DB (e.g., childes) to work with.")
    args = parser.parse_args()
    db = args.db

    # Modeled on this:
    # https://github.com/TalkBank/TBDBpy/blob/146ee4212959d622218cfc9f5f13b1a6737750b0/tbdb/__init__.py#L620-L629
    metadata_url = "https://sla2.talkbank.org:1515/getPathTrees"
    metadata = requests.post(metadata_url).json()["respMsg"]

    if db not in metadata.keys():
        raise ValueError(f"db must be one of {metadata.keys()}: {db}")
    _LOG.info("db: %r", db)

    successes = 0
    failures = 0
    url_prefix = f"https://{db}.talkbank.org/data"

    for corpus, datasets in metadata[db][db].items():
        _LOG.info("Corpus: %r", corpus)
        for dataset in datasets.keys():
            _LOG.info("dataset: %r", dataset)
            if dataset in _HAS_SUBDATASETS.get(db, {}).get(corpus, set()):
                for subdataset in datasets[dataset].keys():
                    url = f"{url_prefix}/{corpus}/{dataset}/{subdataset}.zip"
                    successes, failures = _check_compatibility(url, successes, failures)
            else:
                url = f"{url_prefix}/{corpus}/{dataset}.zip"
                successes, failures = _check_compatibility(url, successes, failures)

    _LOG.info("successes: %r, failures: %r", successes, failures)
