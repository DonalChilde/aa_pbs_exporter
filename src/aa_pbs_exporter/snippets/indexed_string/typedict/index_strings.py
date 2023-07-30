####################################################
#                                                  #
#   src/snippets/indexed_string/typedict/index_strings.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-15T16:11:15-07:00            #
# Last Modified:   #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from collections.abc import Generator
from typing import Callable, Iterable

from aa_pbs_exporter.snippets.indexed_string.typedict.filters import pass_through
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
    indexed_string_factory,
)


def index_strings(
    strings: Iterable[str],
    sieve: Callable[[IndexedStringDict], bool] = pass_through,
    factory: Callable[[int, str], IndexedStringDict] = indexed_string_factory,
    index_start: int = 0,
) -> Generator[IndexedStringDict, None, None]:
    """
    Enumerate a string iterable, yield an `IndexedStringDict`.

    Args:
        strings: An iterable of strings.
        sieve: A filter function that checks wether to approve the indexed string.
        factory: The factory used to make an indexed string. Defaults to IndexedStringDC.
        index_start: The starting index for the strings. Defaults to 0.

    Yields:
        The indexed strings.
    """
    for idx, txt in enumerate(strings, start=index_start):
        idx_str = factory(idx, txt)
        if sieve(idx_str):
            yield idx_str
        else:
            continue


class Indexer:
    def __init__(
        self,
        sieve: Callable[[IndexedStringDict], bool] = pass_through,
        factory: Callable[[int, str], IndexedStringDict] = indexed_string_factory,
        index_start: int = 0,
    ) -> None:
        self.sieve = sieve
        self.factory = factory
        self.index_start = index_start

    def __call__(
        self, strings: Iterable[str]
    ) -> Generator[IndexedStringDict, None, None]:
        return index_strings(
            strings=strings,
            sieve=self.sieve,
            factory=self.factory,
            index_start=self.index_start,
        )
