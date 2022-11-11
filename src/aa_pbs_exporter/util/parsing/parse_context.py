####################################################
#                                                  #
#      src/snippets/parsing/parse_context.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-10T15:45:42-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from abc import ABC, abstractmethod
from typing import TextIO

from aa_pbs_exporter.util.publisher_consumer import MessagePublisher


class ParseContext(ABC):
    def __init__(self, *, source_name: str) -> None:
        self.source_name = source_name

    @abstractmethod
    def handle_parse_result(self, result) -> str:
        pass


class MessengerParseContext(ParseContext):
    def __init__(self, *, source_name: str, messenger: MessagePublisher) -> None:
        super().__init__(source_name=source_name)
        self.messenger = messenger

    @abstractmethod
    def handle_parse_result(self, result) -> str:
        pass


class FileParseContext(ParseContext):
    def __init__(self, *, source_name: str, fp_out: TextIO) -> None:
        super().__init__(source_name=source_name)
        self.fp_out = fp_out

    def handle_parse_result(self, result) -> str:
        self.write_line(str(result))
        return str(result.__class__.__qualname__).lower()

    def write_line(self, line: str):
        self.fp_out.write(line)
        self.fp_out.write("\n")
        self.fp_out.flush()


class DevParseContext(ParseContext):
    def __init__(
        self,
        *,
        source_name: str,
        fp_out: TextIO | None = None,
        wrapped_context: ParseContext | None = None,
    ) -> None:
        super().__init__(source_name=source_name)
        self.fp_out = fp_out
        self.result = None
        self.wrapped_context = wrapped_context
        self.write_line(self.source_name)

    def handle_parse_result(self, result) -> str:
        self.write_line(str(result))
        self.result = result
        if self.wrapped_context is not None:
            return self.wrapped_context.handle_parse_result(result)
        return str(result.__class__.__qualname__).lower()

    def write_line(self, line: str):
        if self.fp_out is not None:
            self.fp_out.write(line)
            self.fp_out.write("\n")
            self.fp_out.flush()
