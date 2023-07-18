####################################################
#                                                  #
# src/snippets/indexed_string/typedict/state_parser/parse_job.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-05-07T11:30:50-07:00            #
# Last Modified:   #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Any, Callable, Iterable, Sequence

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_indexed_strings import (
    parse_indexed_strings,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    CollectedParseResults,
    ResultHandlerProtocol,
)


def parse_job(
    indexed_strings: Iterable[IndexedStringDict],
    parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]],
    result_handler: ResultHandlerProtocol,
    beginning_state: str = "start",
    ctx: dict[str, Any] | None = None,
) -> CollectedParseResults | None:
    with result_handler:
        for parse_result in parse_indexed_strings(
            indexed_strings=indexed_strings,
            parser_lookup=parser_lookup,
            beginning_state=beginning_state,
            ctx=ctx,
        ):
            result_handler.handle_result(parse_result=parse_result, ctx=ctx)
    return result_handler.data
