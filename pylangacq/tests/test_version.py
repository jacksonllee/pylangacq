import os
import re

import pylangacq


_THIS_DIR = os.path.dirname(os.path.realpath(__file__))
_REPO_DIR = os.path.dirname(os.path.dirname(_THIS_DIR))


def test_version_number_match_with_changelog():
    """__version__ and CHANGELOG.md match for the latest version number."""
    with open(os.path.join(_REPO_DIR, "CHANGELOG.md")) as f:
        changelog = f.read()
    # latest version number in changelog = the 1st occurrence of '[x.y.z]'
    changelog_version = re.search(r"\[\d+\.\d+\.\d+\]", changelog).group().strip("[]")
    package_version = pylangacq.__version__
    assert package_version == changelog_version, (
        f"Make sure both __version__ ({package_version}) and CHANGELOG "
        f"({changelog_version}) are updated to match the latest version number"
    )
