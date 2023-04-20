####################################################
#                                                  #
#          src/snippets/file/line_reader.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-15T15:17:37-07:00            #
# Last Modified: 2023-04-15T22:19:17.881469+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from pathlib import Path
from typing import Iterator


def line_reader(file_path: Path) -> Iterator[str]:
    """yield lines in a text file."""
    with open(file_path, encoding="utf-8") as file:
        for line in file:
            yield line
