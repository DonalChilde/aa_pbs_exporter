####################################################
#                                                  #
#     src/snippets/state_parser/state_parser.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-02-05T05:58:53-07:00            #
# Last Modified: 2023-02-05T17:03:55.123337+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from aa_pbs_exporter.snippets.state_parser import state_parser_protocols as spp
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException
from aa_pbs_exporter.snippets.string.indexed_string import IndexedString
from aa_pbs_exporter.snippets.string.indexed_string_protocol import (
    IndexedStringProtocol,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_file(
    file_path: Path,
    manager: spp.ParseManager,
    skipper: Callable[[IndexedStringProtocol], bool] | None = None,
):
    with open(file_path, encoding="utf-8") as file:
        try:
            parse_indexed_strings(file, manager=manager, skipper=skipper)
        except ParseException as error:
            logger.error("%s Failed to parse %r", file_path, error)
            raise error


def parse_string_by_line(
    string_data: str,
    manager: spp.ParseManager,
    skipper: Callable[[IndexedStringProtocol], bool] | None = None,
):
    line_iter = StringIO(string_data)
    parse_indexed_strings(strings=line_iter, manager=manager, skipper=skipper)


def parse_indexed_strings(
    strings: Iterable[str],
    manager: spp.ParseManager,
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
        indexed_string = IndexedString(idx=idx, txt=txt)
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


def parse_indexed_string(
    indexed_string: IndexedStringProtocol,
    parsers: Sequence[spp.IndexedStringParser],
    ctx: dict[str, Any],
) -> spp.ParseResult:
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
