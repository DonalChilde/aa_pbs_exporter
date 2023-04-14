from typing import Callable, Iterable, Iterator

from aa_pbs_exporter.snippets.string.indexed_string import IndexedString
from aa_pbs_exporter.snippets.string.indexed_string_filter import pass_through
from aa_pbs_exporter.snippets.string.indexed_string_protocol import (
    IndexedStringProtocol,
)


def indexed_string_factory(idx: int, txt: str) -> IndexedStringProtocol:
    return IndexedString(idx=idx, txt=txt)


def filtered_indexed_strings(
    strings: Iterable[str],
    string_filter: Callable[[IndexedStringProtocol], bool] = pass_through,
    factory: Callable[[int, str], IndexedStringProtocol] = indexed_string_factory,
) -> Iterator[IndexedStringProtocol]:
    """Filter string iterable, yield matches as IndexedStringProtocol"""
    for idx, txt in enumerate(strings):
        indexed_string = factory(idx=idx, txt=txt)
        if string_filter(indexed_string):
            yield indexed_string
