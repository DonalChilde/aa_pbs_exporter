####################################################
#                                                  #
#  src/snippets/indexed_string/typedict/state_parser/result_handlers.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-06-26T15:59:06-07:00            #
# Last Modified:  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from io import TextIOWrapper
from pathlib import Path
from time import perf_counter_ns

from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser import serialize
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
    ParseResult,
)

# TODO Make a line output handler, and reader. To support files too large for memory.
NANOS_PER_SECOND = 1000000000


def nanos_to_seconds(start: int, end: int) -> float:
    return (end - start) / NANOS_PER_SECOND


class SaveAsJson:
    """convenience class to write completed parse as ResultHandlerData to json file."""

    def __init__(
        self,
        file_out: Path | None = None,
        debug_out: Path | None = None,
        overwrite: bool = False,
        indent: int = 2,
        **kwargs,
    ) -> None:
        """convenience class to write completed parse as ResultHandlerData to json file."""
        self.data: CollectedParseResults | None = {"kwargs": {}, "data": []}
        self.file_out = file_out
        self.overwrite = overwrite
        self.indent = indent
        self.data["kwargs"].update(kwargs)
        self.debug_out = debug_out
        self.debug_fp: TextIOWrapper | None = None
        self.start = 0
        self.end = 0

    def __enter__(self):
        if self.file_out is not None:
            validate_file_out(file_path=self.file_out, overwrite=self.overwrite)
        if self.debug_out is not None:
            validate_file_out(file_path=self.debug_out, overwrite=self.overwrite)
            self.debug_fp = open(self.debug_out, mode="wt", encoding="utf-8")
            if self.data is not None:
                print(repr(self.data["kwargs"]), file=self.debug_fp)
        self.start = perf_counter_ns()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = perf_counter_ns()
        if self.debug_fp is not None:
            print(
                f"complete in {nanos_to_seconds(self.start,self.end)} seconds",
                file=self.debug_fp,
            )
            self.debug_fp.close()
        if self.file_out is not None and self.data is not None:
            serialize.save_as_json(
                file_out=self.file_out,
                parse_results=self.data,
                overwrite=self.overwrite,
                indent=self.indent,
            )

    def handle_result(
        self, parse_result: ParseResult, ctx: dict | None = None, **kwargs
    ):
        """
        Handle the result of a successful parse.

        Args:
            parse_result: The result of a successful parse.
        """
        _ = ctx, kwargs
        if self.debug_fp is not None:
            print(
                f"{parse_result['parse_ident']}"
                f"\n\t{repr(parse_result['parsed_data'])}"
                f"\n\t{repr(parse_result['source'])}",
                file=self.debug_fp,
            )
        if self.data is not None:
            self.data["data"].append(parse_result)


class CollectResults:
    """Collects ParseResults, can debug out to text file or stdout."""

    def __init__(
        self,
        debug: bool = True,
        debug_out: Path | None = None,
        overwrite: bool = False,
        **kwargs,
    ) -> None:
        self.data: CollectedParseResults | None = {"kwargs": {}, "data": []}
        self.debug = debug
        self.debug_out = debug_out
        self.overwrite = overwrite
        self.kwargs = kwargs
        self.debug_fp: TextIOWrapper | None = None
        self.start = 0
        self.end = 0
        self.data["kwargs"].update(kwargs)

    def __enter__(self):
        self.start = perf_counter_ns()
        if self.debug and self.debug_out is not None:
            validate_file_out(file_path=self.debug_out, overwrite=self.overwrite)
            self.debug_fp = open(self.debug_out, mode="wt", encoding="utf-8")
        if self.debug:
            print(repr(self.kwargs), file=self.debug_fp)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = perf_counter_ns()
        if self.debug:
            print(
                f"complete in {nanos_to_seconds(self.start,self.end)} seconds",
                file=self.debug_fp,
            )
        if self.debug_fp is not None:
            self.debug_fp.close()

    def handle_result(
        self, parse_result: ParseResult, ctx: dict | None = None, **kwargs
    ):
        """
        Handle the result of a successful parse.

        Args:
            parse_result: The result of a successful parse.
        """
        _ = ctx, kwargs
        assert self.data is not None
        self.data["data"].append(parse_result)
        if self.debug:
            print(
                f"{parse_result['parse_ident']}"
                f"\n\t{repr(parse_result['parsed_data'])}"
                f"\n\t{repr(parse_result['source'])}",
                file=self.debug_fp,
            )
