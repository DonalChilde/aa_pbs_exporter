####################################################
#                                                  #
# src/snippets/indexed_string/state_parser/result_handler.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-16T08:06:21-07:00            #
# Last Modified: 2023-04-16T16:14:52.916550+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################


from io import TextIOWrapper
from typing import Sequence

from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseResultProtocol,
    ResultHandlerProtocol,
)


class MultipleResultHandler:
    def __init__(self, result_handlers: Sequence[ResultHandlerProtocol]) -> None:
        """
        Contain multiple result handlers.

        Used to pass a parse result to multiple handlers in sequence.

        Args:
            result_handlers: The result handlers.
        """
        self.handlers = list(result_handlers)

    def handle_result(self, parse_result: ParseResultProtocol, **kwargs):
        """Passes the parse result to multiple handlers in sequence."""
        for handler in self.handlers:
            handler.handle_result(parse_result=parse_result, **kwargs)


class SaveToTextFileHandler:
    def __init__(self, writer: TextIOWrapper, record_separator: str = "") -> None:
        """
        Save the parse result to an opened text file.

        Args:
            writer: An opened text file.
            record_separator: A string written between records, eg. `\n`
        """
        self.writer = writer
        self.record_separator = record_separator

    def handle_result(self, parse_result: ParseResultProtocol, **kwargs):
        """Save the parse result to a text file as str(parse_result)."""
        _ = kwargs
        self.writer.write(str(parse_result))
        if self.record_separator:
            self.writer.write(self.record_separator)
