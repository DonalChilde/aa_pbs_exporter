####################################################
#                                                  #
# src/snippets/indexed_string/state_parser/result_handler.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-16T08:06:21-07:00            #
# Last Modified: 2023-04-20T21:42:18.246274+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################


from io import TextIOWrapper
from typing import Sequence

from snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseResultProtocol,
    ResultHandlerProtocol,
)

# TODO make example function that saves all odd numbered input lines to a file.


class MultipleResultHandler:
    def __init__(self, result_handlers: Sequence[ResultHandlerProtocol]) -> None:
        """
        Contain multiple result handlers.

        Used to pass a parse result to multiple handlers in sequence.

        Args:
            result_handlers: The result handlers.
        """
        self.handlers = list(result_handlers)

    def initialize(self, ctx: dict | None = None):
        """Called before the first parse attempt of a parse job."""
        for handler in self.handlers:
            handler.initialize(ctx)

    def handle_result(self, parse_result: ParseResultProtocol, **kwargs):
        """Passes the parse result to multiple handlers in sequence."""
        for handler in self.handlers:
            handler.handle_result(parse_result=parse_result, **kwargs)

    def finalize(self, ctx: dict | None = None):
        """Called after the last chunk of data is parsed."""
        for handler in self.handlers:
            handler.finalize(ctx)


class ParseResultSaveToTextFileHandler:
    def __init__(
        self, writer: TextIOWrapper, record_separator: str = "", as_repr: bool = False
    ) -> None:
        """
        Save the parse result to an opened text file.

        Args:
            writer: An opened text file.
            record_separator: A string written between records, eg. `\n`. Defaults to to ''.
            as_repr: Output as repr(value)
        """
        self.writer = writer
        self.record_separator = record_separator
        self.as_repr = as_repr

    def initialize(self, ctx: dict | None = None):
        """Called before the first parse attempt of a parse job."""
        pass

    def handle_result(self, parse_result: ParseResultProtocol, **kwargs):
        """Save the parse result to a text file as str(parse_result)."""
        _ = kwargs
        if self.as_repr:
            self.writer.write(f"{parse_result!r}")
        else:
            self.writer.write(f"{parse_result}")
        if self.record_separator:
            self.writer.write(self.record_separator)

    def finalize(self, ctx: dict | None = None):
        """Called after the last chunk of data is parsed."""
        pass


class ParsedDataSaveToTextFileHandler:
    def __init__(
        self, writer: TextIOWrapper, record_separator: str = "", as_repr: bool = False
    ) -> None:
        """
        Save the parse_result.parsed_data to an opened text file.

        Args:
            writer: An opened text file.
            record_separator: A string written between records, eg. `\n`. Defaults to to ''.
            as_repr: Output as repr(value)
        """
        self.writer = writer
        self.record_separator = record_separator
        self.as_repr = as_repr

    def initialize(self, ctx: dict | None = None):
        """Called before the first parse attempt of a parse job."""
        pass

    def handle_result(self, parse_result: ParseResultProtocol, **kwargs):
        """Save the parse_result.parsed_data to a text file."""
        _ = kwargs
        if self.as_repr:
            self.writer.write(f"{parse_result.parsed_data!r}")
        else:
            self.writer.write(f"{parse_result.parsed_data}")
        if self.record_separator:
            self.writer.write(self.record_separator)

    def finalize(self, ctx: dict | None = None):
        """Called after the last chunk of data is parsed."""
        pass
