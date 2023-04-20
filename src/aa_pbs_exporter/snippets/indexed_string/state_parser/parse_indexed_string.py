####################################################
#                                                  #
# src/snippets/indexed_string/state_parser/parse_indexed_string.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-16T09:11:27-07:00            #
# Last Modified: 2023-04-16T16:14:52.916266+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
from typing import Any, Sequence

from aa_pbs_exporter.snippets.indexed_string.indexed_string_protocol import (
    IndexedStringProtocol,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_exception import (
    ParseException,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseResultProtocol,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_indexed_string(
    indexed_string: IndexedStringProtocol,
    parsers: Sequence[IndexedStringParserProtocol],
    ctx: dict[str, Any],
) -> ParseResultProtocol:
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
        ParseException: Signals the failure of a parser, or the failure of the parse
            job as a whole.

    Returns:
        The result of a successful parse.
    """
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
