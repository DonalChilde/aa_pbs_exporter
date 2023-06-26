####################################################
#                                                  #
# src/snippets/indexed_string/typedict/state_parser/parse_indexed_strings.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-16T09:11:41-07:00            #
# Last Modified: 2023-06-26T23:11:51.057592+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
from typing import Any, Iterable, Iterator

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseException,
    ParseJobFail,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_indexed_string import (
    parse_indexed_string,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    ParseResult,
    ParserLookupProtocol,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_indexed_strings(
    indexed_strings: Iterable[IndexedString],
    parser_lookup: ParserLookupProtocol,
    ctx: dict[str, Any] | None = None,
) -> Iterator[ParseResult]:
    """
    Parse an iterable of indexed strings.

    Parses an iterable of indexed strings, eg. (idx=linenumber, txt=line) of a text file.
    Uses `state` to predict the possible matches for the next indexed string.
    The beginning state is `start`, and each successful parse will return a new state.
    This new state will be used to get a list of possible matches from the `ParseManager`,
    which will be checked in sequence until a match is found. If no valid matches are
    found, a `ParseException` will be raised, signaling a failure of the parse job.
    In other words, a match must be found for each line.

    Args:
        indexed_strings: An iterable of indexed strings to be parsed.
        manager: The container for expected parsers, and a context variable that can be used
            to store arbitrary info to aid parsing.

    Raises:
        error: Signals a failure of the overall parse job.

    Yields:
        The parse result, which contains the new state, and any parsed data.
    """
    current_state = "start"
    for indexed_string in indexed_strings:
        try:
            parse_result = parse_indexed_string(
                indexed_string=indexed_string,
                parsers=parser_lookup.expected_parsers(current_state),
                ctx=ctx,
            )
            current_state = parse_result["parse_ident"]
            yield parse_result
        except ParseJobFail as error:
            # TODO refine this message
            logger.error("%s", error)
            raise error
        except ParseException as error:
            # TODO unexpected exception, should be ParseAllFail....
            logger.error("%s", error)
            raise error
