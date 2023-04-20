from pathlib import Path
from typing import Callable, Iterable, Sequence

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.result_handler import AssembleRawBidPackage
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
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
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_indexed_strings import (
    parse_indexed_strings,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.result_handler import (
    MultipleResultHandler,
    ParsedDataSaveToTextFileHandler,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseManagerProtocol,
    ResultHandlerProtocol,
)


def data_starts(indexed_string: IndexedStringProtocol) -> bool:
    if "DEPARTURE" in indexed_string.txt:
        return True
    return False


def pbs_data() -> Callable[[IndexedStringProtocol], bool]:
    return MultipleTests(
        testers=[SkipTillFirstMatch(match_test=data_starts), not_white_space]
    )


def indexed_string_factory(idx: int, txt: str) -> IndexedStringProtocol:
    return raw.IndexedString(idx=idx, txt=txt)


def index_pbs_data(strings: Iterable[str]) -> Iterable[IndexedStringProtocol]:
    indexed_strings = index_and_filter_strings(
        strings=strings, string_filter=pbs_data(), factory=indexed_string_factory
    )
    return indexed_strings


def parse_pbs_data(
    strings: Iterable[str],
    manager: ParseManagerProtocol,
    result_handler: ResultHandlerProtocol,
):
    indexed_strings = index_pbs_data(strings)
    result_handler.initialize(manager.ctx)
    for parse_result in parse_indexed_strings(
        indexed_strings=indexed_strings, manager=manager
    ):
        result_handler.handle_result(parse_result)
    result_handler.finalize(manager.ctx)


def parse_raw_bidpackage(
    strings: Iterable[str],
    manager: ParseManagerProtocol,
    source: str,
    additional_handlers: Sequence[ResultHandlerProtocol] | None = None,
) -> raw.BidPackage:
    if additional_handlers is None:
        additional_handlers = []
    package_handler = AssembleRawBidPackage(source=source)
    handler = MultipleResultHandler(result_handlers=additional_handlers)
    handler.handlers.append(package_handler)
    parse_pbs_data(strings=strings, manager=manager, result_handler=handler)
    return package_handler.bid_package


def debug_parse_raw_bidpackage(
    strings: Iterable[str],
    manager: ParseManagerProtocol,
    source: str,
    debug_file_path: Path,
    additional_handlers: Sequence[ResultHandlerProtocol] | None = None,
) -> raw.BidPackage:
    validate_file_out(debug_file_path)
    with open(debug_file_path, "w", encoding="utf-8") as debug_file:
        debug_file.write(f"source: {source}\n")
        debug_handler = ParsedDataSaveToTextFileHandler(debug_file, "\n")
        handlers: list[ResultHandlerProtocol] = [debug_handler]
        if additional_handlers is not None:
            handlers.extend(additional_handlers)
        try:
            result = parse_raw_bidpackage(
                strings=strings,
                manager=manager,
                source=source,
                additional_handlers=handlers,
            )
        except Exception as error:
            debug_file.write(str(error))
            raise error
        return result
