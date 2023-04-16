####################################################
#                                                  #
# src/snippets/indexed_string/index_and_filter_strings.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-15T16:11:28-07:00            #
# Last Modified: 2023-04-16T16:14:52.917117+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Callable, Iterable, Iterator

from aa_pbs_exporter.snippets.indexed_string.indexed_string_dc import IndexedStringDC
from aa_pbs_exporter.snippets.indexed_string.indexed_string_protocol import (
    IndexedStringProtocol,
)


def index_and_filter_strings(
    strings: Iterable[str],
    string_filter: Callable[[IndexedStringProtocol], bool],
    factory: Callable[[int, str], IndexedStringProtocol] = IndexedStringDC,
    index_start=0,
) -> Iterator[IndexedStringProtocol]:
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
        indexed_string = factory(idx, txt)
        if string_filter(indexed_string):
            yield indexed_string
