from __future__ import annotations

import os

from typing import Sequence

from rustling.chat import CHAT


def read_chat(
    path: str,
    *,
    filter_files: str | Sequence[str] | None = None,
    filter_participants: str | Sequence[str] | None = None,
    cls: type = CHAT,
    strict: bool = True,
) -> CHAT:
    """Read CHAT data.

    Args:
        path: Path to a ``.zip`` file, a local directory containing ``.cha``
            files, or a single ``.cha`` file.
        filter_files: Filename(s) to keep.
            Regular expression matching is supported.
            If ``None``, all files are included.
        filter_participants: Participant code(s) to keep.
            Regular expression matching is supported.
            If ``None``, all participants are included.
        cls: The class used to create the reader. Must be ``CHAT`` or a
            subclass of it.
        strict: If ``True``, enforce strict parsing of the CHAT data.

    Returns:
        A ``CHAT`` instance filtered by the specified files and participants.

    Raises:
        TypeError: If *cls* is not ``CHAT`` or a subclass of it.
        ValueError: If *path* does not point to a ``.zip`` file, a directory,
            or a ``.cha`` file.
    """
    if cls != CHAT and not issubclass(cls, CHAT):
        raise TypeError(f"Only a CHAT class or its child class is allowed: {cls}")

    path_lower = path.lower()
    if path_lower.endswith(".zip"):
        return cls.from_zip(
            path,
            strict=strict,
        ).filter(files=filter_files, participants=filter_participants)
    elif os.path.isdir(path):
        return cls.from_dir(
            path,
            strict=strict,
        ).filter(files=filter_files, participants=filter_participants)
    elif path_lower.endswith(".cha"):
        return cls.from_files(
            [path],
            strict=strict,
        ).filter(files=filter_files, participants=filter_participants)
    else:
        raise ValueError(
            "path is not one of the accepted choices of "
            f"{{.zip file, local directory, .cha file}}: {path}"
        )
