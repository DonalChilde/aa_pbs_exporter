from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

# from aa_pbs_exporter.pbs_2022_01.models import raw
# from aa_pbs_exporter.pbs_2022_01.parser.parse_manager import ParseManager
from aa_pbs_exporter.snippets.indexed_string.typedict.filters import (
    MultipleTests,
    SkipTillFirstMatch,
    not_white_space,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.result_handlers import (
    SaveAsJson,
)
from aa_pbs_exporter.snippets.timers import timers
from aa_pbs_exporter.snippets.indexed_string.typedict.index_and_filter_strings import (
    index_and_filter_strings,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
    indexed_string_factory,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_job import (
    parse_job,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseResult,
    CollectedParseResults,
    ResultHandlerProtocol,
)
import logging

logger = logging.getLogger(__name__)


def data_starts(indexed_string: IndexedString) -> bool:
    if "DEPARTURE" in indexed_string["txt"]:
        return True
    return False


def pbs_data_filter() -> Callable[[IndexedString], bool]:
    return MultipleTests(
        testers=[SkipTillFirstMatch(match_test=data_starts), not_white_space]
    )


def index_pbs_strings(strings: Iterable[str]) -> Iterable[IndexedString]:
    indexed_strings = index_and_filter_strings(
        strings=strings, string_filter=pbs_data_filter(), factory=indexed_string_factory
    )
    return indexed_strings


# def parse_pbs_strings(
#     strings: Iterable[str],
#     parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]],
#     result_handler: ResultHandlerProtocol,
#     ctx: dict[str, Any] | None = None,
# ) -> ResultHandlerData | None:
#     indexed_strings = index_pbs_strings(strings)
#     result = parse_job(
#         indexed_strings=indexed_strings,
#         parser_lookup=parser_lookup,
#         result_handler=result_handler,
#         ctx=ctx,
#     )
#     return result
