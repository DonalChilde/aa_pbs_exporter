from typing import Callable, Iterable

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.parser.parse_manager import ParseManager
from aa_pbs_exporter.snippets.indexed_string.filters import (
    MultipleTests,
    SkipTillFirstMatch,
    not_white_space,
)
from aa_pbs_exporter.snippets.indexed_string.index_and_filter_strings import (
    index_and_filter_strings,
)
from aa_pbs_exporter.snippets.indexed_string.indexed_string_protocol import (
    IndexedStringProtocol,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_job import parse_job


def data_starts(indexed_string: IndexedStringProtocol) -> bool:
    if "DEPARTURE" in indexed_string.txt:
        return True
    return False


def pbs_data_filter() -> Callable[[IndexedStringProtocol], bool]:
    return MultipleTests(
        testers=[SkipTillFirstMatch(match_test=data_starts), not_white_space]
    )


def indexed_string_factory(idx: int, txt: str) -> IndexedStringProtocol:
    return raw.IndexedString(idx=idx, txt=txt)


def index_pbs_strings(strings: Iterable[str]) -> Iterable[IndexedStringProtocol]:
    indexed_strings = index_and_filter_strings(
        strings=strings, string_filter=pbs_data_filter(), factory=indexed_string_factory
    )
    return indexed_strings


def parse_pbs_strings(
    strings: Iterable[str],
    manager: ParseManager[raw.BidPackage],
) -> raw.BidPackage | None:
    indexed_strings = index_pbs_strings(strings)
    # This is the lowest level interface with the state parser code.
    # Here is the place to initialize any resources managed by the parse manager.
    with manager:
        result = parse_job(indexed_strings=indexed_strings, manager=manager)
    return result
