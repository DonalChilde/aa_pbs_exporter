####################################################
#                                                  #
#    src/snippets/file/validate_file_out.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-29T09:11:28-07:00            #
# Last Modified: 2022-12-03T23:49:38.693575+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from pathlib import Path


def validate_file_out(
    file_path: Path, overwrite: bool, *, ensure_parent: bool = True
) -> bool:
    """Ensure that a file path is suitable for output.

    Optionally can ensure that parent directories exist.
    """
    if file_path.is_dir():
        raise ValueError(
            f"{file_path} is an invalid destination. It is an existing directory."
        )
    if not overwrite and file_path.is_file():
        raise ValueError(
            f"{file_path} is an invalid destination. "
            "It is an existing file and overwrite was not selected."
        )
    if ensure_parent:
        parent = file_path.parent
        parent.mkdir(parents=True, exist_ok=True)
    return file_path.parent.is_dir()
