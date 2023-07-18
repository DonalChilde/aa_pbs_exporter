from io import TextIOWrapper
from pathlib import Path
from typing import Callable, Iterable

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)


class IndexFile:
    def __init__(
        self,
        file_in: Path,
        indexer: Callable[[Iterable[str]], Iterable[IndexedStringDict]],
    ) -> None:
        self.file_in = file_in
        self.indexer = indexer
        self.file_fp: TextIOWrapper | None = None

    def __enter__(self) -> Iterable[IndexedStringDict]:
        self.file_fp = open(self.file_in, mode="rt", encoding="utf-8")
        for item in self.indexer(self.file_fp):
            yield item

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file_fp is not None:
            self.file_fp.close()
