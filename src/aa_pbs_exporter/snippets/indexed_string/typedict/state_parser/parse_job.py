####################################################
#                                                  #
# src/snippets/indexed_string/typedict/state_parser/parse_job.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-05-07T11:30:50-07:00            #
# Last Modified: 2023-06-26T23:11:51.057861+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Any, Iterable, TypeVar

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_indexed_strings import (
    parse_indexed_strings,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    ParserLookupProtocol,
    ResultHandlerData,
    ResultHandlerProtocol,
)

T = TypeVar("T")


def parse_job(
    indexed_strings: Iterable[IndexedString],
    parser_lookup: ParserLookupProtocol,
    result_handler: ResultHandlerProtocol,
    ctx: dict[str, Any] | None = None,
) -> ResultHandlerData | None:
    with result_handler:
        for parse_result in parse_indexed_strings(
            indexed_strings=indexed_strings, parser_lookup=parser_lookup, ctx=ctx
        ):
            result_handler.handle_result(parse_result=parse_result, ctx=ctx)
    return result_handler.data
