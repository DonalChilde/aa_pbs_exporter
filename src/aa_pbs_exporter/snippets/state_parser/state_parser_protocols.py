####################################################
#                                                  #
# src/snippets/state_parser/state_parser_protocols.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-02-05T05:59:13-07:00            #
# Last Modified: 2023-02-05T17:03:55.124038+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
"""
Defines the interface for a state based text parser.

When parsing semi structured text, parsing a section often depends on
knowing what the previous section was.
"""

# FIXME Change this to Indexed String Parser Protocol, as that is a defining
#   factor more than state.
# TODO put protocol in all the names?

from typing import Any, Protocol, Sequence

from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException
from aa_pbs_exporter.snippets.string.indexed_string_protocol import (
    IndexedStringProtocol,
)


class ParsedIndexedStringProtocol(Protocol):
    """Contains data parsed from an `IndexedStringProtocol`.

    This class is usually subclassed to represent the source string, and the
    parsed result.

    Attributes:
        source: The IndexedString that was parsed.
    """

    source: IndexedStringProtocol


class ParseResultProtocol(Protocol):
    """The result of a successful parse.

    Attributes:
        current_state: The current state of the parser.
        parsed_data: The data parsed from an `IndexedStringProtocol`

    """

    current_state: str
    parsed_data: Any


class IndexedStringParserProtocol(Protocol):
    """Parse an IndexedString."""

    def parse(
        self,
        indexed_string: IndexedStringProtocol,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        """
        A parse function that matches an IndexedString.

        Raise ParseException on a parse error. Pass any additional information
        required in the ctx. A successful parse also determines the new state of the
        parse job.

        Args:
            indexed_string: The IndexedString to be parsed.
            ctx: A dictionary that holds any additional information needed for parsing.

        Raises:
            ParseException: Raises a ParseException for a failed parse.

        Returns:
            The `ParseResult` of a successful parse.
        """
        raise ParseException


class ResultHandlerProtocol(Protocol):
    """Do something with the result of a successful parse."""

    def handle_result(self, parse_result: ParseResultProtocol, **kwargs):
        ...


class ParseSchemeProtocol(Protocol):
    """Get a list of parsers expected to match the next string.

    The state string is usually obtained during the previous parse, where a successful
    parse determines the new current state of the parse job.
    """

    def expected_parsers(
        self, current_state: str, **kwargs
    ) -> Sequence[IndexedStringParserProtocol]:
        ...


class ParseManagerProtocol(Protocol):
    """Holds references to the ResultHandler, ExpectedParsers, and a context dict."""

    ctx: dict[str, Any]
    result_handler: ResultHandlerProtocol
    parse_scheme: ParseSchemeProtocol

    def expected_parsers(
        self, current_state: str, **kwargs
    ) -> Sequence[IndexedStringParserProtocol]:
        ...

    def handle_result(self, parse_result: ParseResultProtocol, **kwargs):
        ...
