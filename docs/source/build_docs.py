#!/usr/bin/env python

"""This script updates the documentation website."""

import logging
import os

import m2r


_DOCS_SOURCE = os.path.dirname(os.path.abspath(__file__))
_DOCS = os.path.dirname(_DOCS_SOURCE)
_REPO_ROOT = os.path.dirname(_DOCS)


def remove_generated_docs():
    logging.info("Removing generated docs")
    os.system(f"rm {os.path.join(_DOCS, '*.html')}")
    os.system(f"rm -rf {os.path.join(_DOCS, '_sources')}")
    os.system(f"rm -rf {os.path.join(_DOCS, '_modules')}")
    os.system(f"rm -rf {os.path.join(_DOCS, '_static')}")
    os.system(f"rm -rf {os.path.join(_DOCS, '.doctrees')}")
    os.system(f"rm -rf {os.path.join(_DOCS, '_generated')}")
    os.system(f"rm -rf {os.path.join(_DOCS_SOURCE, '_generated')}")


def rebuild_docs():
    logging.info("Rebuilding docs")
    os.system(f"sphinx-build -b html {_DOCS_SOURCE} {_DOCS}")


def create_changelog_rst():
    logging.info("Creating changelog.rst")
    with open(os.path.join(_REPO_ROOT, "CHANGELOG.md"), encoding="utf8") as f:
        changelog_md = f.read()
    changelog_rst = (
        ".. _changelog:\n\n"
        + "Changelog\n=========\n"
        + m2r.convert(changelog_md[changelog_md.index("## [Unreleased]") :])
    )
    with open(os.path.join(_DOCS_SOURCE, "changelog.rst"), "w", encoding="utf8") as f:
        f.write(changelog_rst)


def create_robots_txt():
    logging.info("Creating robots.txt")
    with open(os.path.join(_DOCS, "robots.txt"), "w", encoding="utf8") as f:
        f.write("User-agent: *\n\nSitemap: https://pylangacq.org/sitemap.xml\n")


def add_custom_css():
    logging.info("Adding custom css")
    dir_ = os.path.join(_DOCS, "_static")
    os.makedirs(dir_, exist_ok=True)
    file_path = os.path.join(dir_, "custom.css")
    with open(file_path, "w", encoding="utf-8") as f:
        # https://stackoverflow.com/q/69873561
        avoid_uppercasing_docstrings = """
dl.py .field-list dt {
    text-transform: none !important;
}
        """
        f.write(avoid_uppercasing_docstrings)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    remove_generated_docs()
    create_changelog_rst()
    create_robots_txt()
    add_custom_css()
    # Rebuilding docs has to be the final step.
    rebuild_docs()
