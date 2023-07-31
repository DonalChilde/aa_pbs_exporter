####################################################
#                                                  #
# src/snippets/indexed_string/typedict/state_parser/parse_indexed_string.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-16T09:11:27-07:00            #
# Last Modified:   #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
from typing import Any, Sequence

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseAllFail,
    ParseJobFail,
    SingleParserFail,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseResult,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_indexed_string(
    indexed_string: IndexedStringDict,
    parsers: Sequence[IndexedStringParserProtocol],
    ctx: dict[str, Any] | None,
    debug_info: str = "",
) -> ParseResult:
    """
    Parse an indexed string based on a list of possible parsers.

    The failure of an individual parser should raise a `ParseException`. This does not
    represent a failure of the parse job as a whole, unless none of the parses
    successfully match.

    Args:
        indexed_string: An indexed string to parse.
        parsers: A sequence of parsers to try.
        ctx: A store for arbitrary information needed to parse.

    Raises:
        SingleParserFail: Signals the failure of a parser.
        ParseJobFail: Signals the failure of the parse job as a whole.
        ParseAllFail: Signals the failure of all parsers.

    Returns:
        The result of a successful parse.
    """
    for parser in parsers:
        try:
            parse_result = parser.parse(indexed_string=indexed_string, ctx=ctx)
            return parse_result
        except SingleParserFail as error:
            logger.debug(
                "\n\tFAILED %r->%r\n\t%r\n\tDebug Info:%r",
                error.parser.__class__.__name__,
                error.indexed_string,
                error,
                debug_info,
            )
        except ParseJobFail as error:
            logger.error("Parse Job failed %s Debug Info:%r", error, debug_info)
            raise error
    raise ParseAllFail(
        f"No parser found for \n\tindexed_string={indexed_string!r}"
        f"\n\tTried {parsers!r}\n\tDebug Info:{debug_info}",
        parsers=parsers,
        indexed_string=indexed_string,
    )
