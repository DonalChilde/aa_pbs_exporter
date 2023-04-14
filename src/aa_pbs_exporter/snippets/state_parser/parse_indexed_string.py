import logging
from typing import Any, Sequence

from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException
from aa_pbs_exporter.snippets.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseResultProtocol,
)
from aa_pbs_exporter.snippets.string.indexed_string_protocol import (
    IndexedStringProtocol,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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
