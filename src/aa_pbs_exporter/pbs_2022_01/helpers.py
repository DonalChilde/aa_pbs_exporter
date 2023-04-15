from io import StringIO
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Sequence

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.parse_manager import ParseManager
from aa_pbs_exporter.pbs_2022_01.parse_scheme import ParseScheme
from aa_pbs_exporter.pbs_2022_01.parsers import logger
from aa_pbs_exporter.pbs_2022_01.result_handler import ResultHandler
from aa_pbs_exporter.snippets.file.line_reader import line_reader
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException
from aa_pbs_exporter.snippets.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseManagerProtocol,
    ParseResultProtocol,
)
from aa_pbs_exporter.snippets.string.filtered_indexed_strings import (
    filtered_indexed_strings,
)
from aa_pbs_exporter.snippets.string.indexed_string_filter import (
    MultiTest,
    SkipBlankLines,
    SkipTillMatch,
)
from aa_pbs_exporter.snippets.string.indexed_string_protocol import (
    IndexedStringProtocol,
)


def data_starts(indexed_string: IndexedStringProtocol) -> bool:

    if "DEPARTURE" in indexed_string.txt:
        return True
    return False


def make_skipper() -> Callable[[IndexedStringProtocol], bool]:
    return MultiTest(testers=[SkipTillMatch(matcher=data_starts), SkipBlankLines()])


def parse_indexed_string(
    indexed_string: IndexedStringProtocol,
    parsers: Sequence[IndexedStringParserProtocol],
    ctx: dict[str, Any],
) -> ParseResultProtocol:
    for parser in parsers:
        try:
            parse_result = parser.parse(indexed_string=indexed_string, ctx=ctx)
            logger.info("\n\tPARSED %r->%r", parser.__class__.__name__, indexed_string)
            return parse_result
        except ParseException as error:
            logger.info(
                "\n\tFAILED %r->%r\n\t%r",
                parser.__class__.__name__,
                indexed_string,
                error,
            )
    raise ParseException(f"No parser found for {indexed_string!r}\nTried {parsers!r}")


def parse_indexed_strings(
    strings: Iterable[str],
    manager: ParseManagerProtocol,
    skipper: Callable[[IndexedStringProtocol], bool] | None = None,
):
    """
    Parse a string iterable.
    Args:
        strings: _description_
        manager: _description_
        skipper: _description_. Defaults to None.
    Raises:
        error: _description_
    """
    current_state = "start"
    for idx, txt in enumerate(strings):
        indexed_string = raw.IndexedString(idx=idx, txt=txt)
        if skipper is not None and not skipper(indexed_string):
            continue
        try:
            parse_result = parse_indexed_string(
                indexed_string=indexed_string,
                parsers=manager.expected_parsers(current_state),
                ctx=manager.ctx,
            )
            manager.handle_result(parse_result=parse_result)
            current_state = parse_result.current_state
        except ParseException as error:
            logger.error("%s", error)
            raise error


def parse_file(file_path: Path) -> raw.BidPackage:
    scheme = ParseScheme()
    result_handler = ResultHandler(source=str(file_path))
    skipper = make_skipper()
    manager = ParseManager(ctx={}, result_handler=result_handler, parse_scheme=scheme)
    with open(file_path, encoding="utf-8") as file:
        try:
            parse_indexed_strings(file, manager=manager, skipper=skipper)
        except ParseException as error:
            logger.error("%s Failed to parse %r", file_path, error)
            raise error
    return result_handler.bid_package


def parse_string_by_line(source: str, string_data: str) -> raw.BidPackage:
    scheme = ParseScheme()
    result_handler = ResultHandler(source=str(source))
    skipper = make_skipper()
    manager = ParseManager(ctx={}, result_handler=result_handler, parse_scheme=scheme)
    line_iter = StringIO(string_data)
    parse_indexed_strings(strings=line_iter, manager=manager, skipper=skipper)
    return result_handler.bid_package


def parsed_index_string_reader(
    indexed_strings: Iterable[IndexedStringProtocol],
    manager: ParseManagerProtocol,
) -> Iterator[ParseResultProtocol]:
    current_state = "start"
    for indexed_string in indexed_strings:
        try:
            parse_result = parse_indexed_string(
                indexed_string=indexed_string,
                parsers=manager.expected_parsers(current_state),
                ctx=manager.ctx,
            )
            # manager.handle_result(parse_result=parse_result)
            current_state = parse_result.current_state
            yield parse_result
        except ParseException as error:
            logger.error("%s", error)
            raise error


def indexed_string_factory(idx: int, txt: str) -> IndexedStringProtocol:
    return raw.IndexedString(idx=idx, txt=txt)


def parse_file_2(file_path: Path, debug_path: Path) -> raw.BidPackage:
    scheme = ParseScheme()
    result_handler = ResultHandler(source=str(file_path))
    skipper = make_skipper()
    manager = ParseManager(ctx={}, result_handler=result_handler, parse_scheme=scheme)
    input_file = line_reader(file_path)
    indexed_strings = filtered_indexed_strings(
        input_file, string_filter=skipper, factory=indexed_string_factory
    )
    for parse_result in parsed_index_string_reader(
        indexed_strings=indexed_strings, manager=manager
    ):
        # debug out to csv here
        manager.handle_result(parse_result=parse_result)
    return result_handler.bid_package


def parse_file_3(
    file_path: Path,
    manager: ParseManagerProtocol,
    string_filter: Callable[[IndexedStringProtocol], bool],
    factory: Callable[[int, str], IndexedStringProtocol],
) -> Iterable[ParseResultProtocol]:
    input_file = line_reader(file_path)
    indexed_strings = filtered_indexed_strings(
        input_file, string_filter=string_filter, factory=factory
    )
    for parse_result in parsed_index_string_reader(
        indexed_strings=indexed_strings, manager=manager
    ):
        yield parse_result
