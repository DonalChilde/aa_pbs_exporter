import logging
from typing import Iterable, Iterator

from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException
from aa_pbs_exporter.snippets.state_parser.parse_indexed_string import (
    parse_indexed_string,
)
from aa_pbs_exporter.snippets.state_parser.state_parser_protocols import (
    ParseManagerProtocol,
    ParseResultProtocol,
)
from aa_pbs_exporter.snippets.string.indexed_string_protocol import (
    IndexedStringProtocol,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parsed_indexed_strings(
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
