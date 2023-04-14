from pathlib import Path
from typing import Iterator


def line_reader(file_path: Path) -> Iterator[str]:
    """yield lines in a text file."""
    with open(file_path, encoding="utf-8") as file:
        for line in file:
            yield line