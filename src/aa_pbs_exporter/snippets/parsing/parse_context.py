####################################################
#                                                  #
#      src/snippets/parsing/parse_context.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-10T15:45:42-07:00            #
# Last Modified: 2022-12-03T23:51:03.919474+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from abc import ABC, abstractmethod
from typing import TextIO, TypeVar

T = TypeVar("T")


class ParseContext(ABC):
    def __init__(self, *, source_name: str, results_obj=None) -> None:
        self.source_name = source_name
        self._results_obj = results_obj

    @abstractmethod
    def handle_parse_result(self, result) -> str:
        pass

    @property
    def results_obj(self):
        return self._results_obj

    @results_obj.setter
    def results_obj(self, value):
        self._results_obj = value


class NoOpParseContext(ParseContext):
    def handle_parse_result(self, result) -> str:
        return str(result.__class__.__qualname__)


class FileParseContext(ParseContext):
    def __init__(self, *, source_name: str, fp_out: TextIO, results_obj=None) -> None:
        super().__init__(source_name=source_name, results_obj=results_obj)
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
        wrapped_context: ParseContext,
        results_obj=None,
        fp_out: TextIO | None = None,
    ) -> None:
        super().__init__(source_name=source_name, results_obj=results_obj)
        self.fp_out = fp_out
        self.result = None
        self.wrapped_context = wrapped_context
        self.write_line(self.source_name)

    def handle_parse_result(self, result) -> str:
        self.write_line(str(result))
        self.result = result
        return self.wrapped_context.handle_parse_result(result)

    def write_line(self, line: str):
        if self.fp_out is not None:
            self.fp_out.write(line)
            self.fp_out.write("\n")
            self.fp_out.flush()

    @property
    def results_obj(self):
        return self.wrapped_context.results_obj

    @results_obj.setter
    def results_obj(self, value):
        self.wrapped_context.results_obj = value
