####################################################
#                                                  #
# src/snippets/indexed_string/typedict/index_and_filter_strings.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-15T16:11:28-07:00            #
# Last Modified: 2023-06-26T23:11:51.059632+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Callable, Iterable, Iterator

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)


def index_and_filter_strings(
    strings: Iterable[str],
    string_filter: Callable[[IndexedStringDict], bool],
    factory: Callable[[int, str], IndexedStringDict] | None = None,
    index_start=0,
) -> Iterator[IndexedStringDict]:
    """
    Enumerate and filter a string iterable, yield matches as an `IndexedStringProtocol`

    Args:
        strings: An iterable of strings.
        string_filter: Used to test strings.
        factory: The factory used to make an indexed string. Defaults to IndexedStringDC.
        index_start: Defaults to 0.

    Yields:
        The matched indexed strings.
    """
    for idx, txt in enumerate(strings, start=index_start):
        if factory is None:
            indexed_string = IndexedStringDict(idx=idx, txt=txt)
        else:
            indexed_string = factory(idx, txt)
        if string_filter(indexed_string):
            yield indexed_string


class FilteredStringIndexer:
    def __init__(
        self,
        string_filter: Callable[[IndexedStringDict], bool],
        factory: Callable[[int, str], IndexedStringDict] | None = None,
        index_start=0,
    ) -> None:
        self.string_filter = string_filter
        self.factory = factory
        self.index_start = index_start

    def __call__(self, strings: Iterable[str]) -> Iterator[IndexedStringDict]:
        for idx, txt in enumerate(strings, start=self.index_start):
            if self.factory is None:
                indexed_string = IndexedStringDict(idx=idx, txt=txt)
            else:
                indexed_string = self.factory(idx, txt)
            if self.string_filter(indexed_string):
                yield indexed_string
