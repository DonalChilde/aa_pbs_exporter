####################################################
#                                                  #
# src/snippets/indexed_string/state_parser/state_parser_protocols.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-02-05T05:59:13-07:00            #
# Last Modified: 2023-04-20T21:42:18.247003+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
"""
Defines the interface for a state based indexed string parser.

When parsing semi structured text, parsing a section often depends on
knowing what the previous section was. This parser allows the selection of possible
parsers based on the results of the previous successfully parsed string.
"""
from typing import Any, Protocol, Sequence

from snippets.indexed_string.indexed_string_protocol import IndexedStringProtocol
from snippets.indexed_string.state_parser.parse_exception import ParseException


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
        self, indexed_string: IndexedStringProtocol, ctx: dict[str, Any], **kwargs
    ) -> ParseResultProtocol:
        """
        A parse function that matches an IndexedString.

        Raise ParseException on a parse error. Pass any additional information
        required in the ctx. A successful parse also determines the new state of the
        parse job.

        Args:
            indexed_string: The indexed string to be parsed.
            ctx: A dictionary that holds any additional information needed for parsing.

        Raises:
            ParseException: Raises a ParseException for a failed parse.

        Returns:
            The `ParseResult` of a successful parse.
        """
        raise ParseException


class ResultHandlerProtocol(Protocol):
    """Do something with a parse result."""

    def initialize(self, ctx: dict | None = None):
        """Called before the first parse attempt of a parse job."""
        raise NotImplementedError

    def handle_result(
        self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
    ):
        """
        Handle the result of a successful parse.

        Args:
            parse_result: The result of a successful parse.
        """
        raise NotImplementedError

    def finalize(self, ctx: dict | None = None):
        """Called after the last chunk of data is parsed."""
        raise NotImplementedError


# class ExpectedParsersProtocol(Protocol):
#     """Get a list of parsers expected to match the next string.

#     The state string is usually updated during the previous parse, where a successful
#     parse determines the new current state of the parse job.
#     """

#     def expected_parsers(
#         self, current_state: str, **kwargs
#     ) -> Sequence[IndexedStringParserProtocol]:
#         """
#         Get a seqence of parsers expected to match the next indexed string parsed.

#         Args:
#             current_state: The current state of a parse job.

#         Returns:
#             The sequence of parsers.
#         """
#         raise NotImplementedError


class ParseManagerProtocol(Protocol):
    """
    Contains the information needed to parse indexed strings.

    Provides parsers expected to match the next indexed string based on the `state` from
    the previous successful parse. The `start` state typically represents the state
    of the job before any parsing takes place.

    Attributes:
        ctx: A store for arbitrary information needed to parse. Can be used to pass information
            between parsers.
    """

    ctx: dict[str, Any]

    def expected_parsers(
        self, state: str, **kwargs
    ) -> Sequence[IndexedStringParserProtocol]:
        """
        Get a sequence of parsers expected to match the next indexed string.

        The parsers returned are based on the current state of a parse job.

        Args:
            state: The current state of a parse job.

        Returns:
            A sequence of parsers expected to match the next indexed string.
        """
        raise NotImplementedError
