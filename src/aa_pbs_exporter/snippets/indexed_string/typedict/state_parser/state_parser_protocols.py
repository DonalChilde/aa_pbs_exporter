####################################################
#                                                  #
# src/snippets/indexed_string/typedict/state_parser/state_parser_protocols.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-02-05T05:59:13-07:00            #
# Last Modified: 2023-06-26T23:11:51.056598+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
"""
Defines the interface for a state based indexed string parser.

When parsing semi structured text, parsing a section often depends on
knowing what the previous section was. This parser allows the selection of possible
parsers based on the results of the previous successfully parsed string.
"""
from typing import Any, Protocol, Sequence, TypedDict, TypeVar

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
)

T = TypeVar("T")


class ParseResult(TypedDict):
    parse_ident: str
    parsed_data: dict[str, Any]
    source: IndexedString


class ResultHandlerData(TypedDict):
    kwargs: dict[str, Any]
    data: list[ParseResult]


# class ParsedIndexedStringProtocol(Protocol):
#     """Contains data parsed from an `IndexedStringProtocol`.

#     This class is usually subclassed to represent the source string, and the
#     parsed result.

#     Attributes:
#         source: The IndexedString that was parsed.
#     """

#     source: IndexedStringProtocol


# class ParseResultProtocol(Protocol):
#     """The result of a successful parse.

#     Attributes:
#         current_state: The current state of the parser.
#         parsed_data: The data parsed from an `IndexedStringProtocol`

#     """

#     current_state: str
#     parsed_data: Any


class IndexedStringParserProtocol(Protocol):
    """Parse an IndexedString."""

    def parse(
        self,
        indexed_string: IndexedString,
        ctx: dict[str, Any] | None,
        **kwargs,
    ) -> ParseResult:
        """
        A parse function that matches an IndexedString.

        Raise ParseFail on a parse error. Pass any additional information
        required in the ctx. A successful parse also determines the new state of the
        parse job.

        Args:
            indexed_string: The indexed string to be parsed.
            ctx: A dictionary that holds any additional information needed for parsing.

        Raises:
            ParseFail: Raises a ParseFail exception for a failed parse.
            ParseAllFail: Raised to kill a parse job from inside an indiviual parser.

        Returns:
            The `ParseResult` of a successful parse.
        """
        raise NotImplementedError


class ResultHandlerProtocol(Protocol):
    """Do something with a parse result."""

    data: ResultHandlerData | None

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def handle_result(
        self, parse_result: ParseResult, ctx: dict | None = None, **kwargs
    ):
        """
        Handle the result of a successful parse.

        Args:
            parse_result: The result of a successful parse.
        """
        raise NotImplementedError


class ParserLookupProtocol(Protocol):
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


# class ParseManagerProtocol(Protocol[T]):
#     """
#     Contains the information needed to parse indexed strings.

#     Provides parsers expected to match the next indexed string based on the `state` from
#     the previous successful parse. The `start` state typically represents the state
#     of the job before any parsing takes place.

#     Attributes:
#         ctx: A store for arbitrary information needed to parse. Can be used to pass information
#             between parsers.
#     """

#     ctx: dict[str, Any] | None

#     def expected_parsers(
#         self, state: str, **kwargs
#     ) -> Sequence[IndexedStringParserProtocol]:
#         """
#         Get a sequence of parsers expected to match the next indexed string.

#         The parsers returned are based on the current state of a parse job.

#         Args:
#             state: The current state of a parse job.

#         Returns:
#             A sequence of parsers expected to match the next indexed string.
#         """
#         raise NotImplementedError

#     def result_handler(self) -> ResultHandlerProtocol[T]:
#         ...
