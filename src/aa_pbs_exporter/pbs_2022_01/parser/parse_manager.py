from io import TextIOWrapper
from pathlib import Path
from typing import Any, Dict, Generic, Self, Sequence, TypeVar

from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme import parse_scheme as scheme
from aa_pbs_exporter.pbs_2022_01.parser.result_handlers.raw_parse_handler import (
    RawResultHandler,
)
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
)

T = TypeVar("T")


class ParseManager(Generic[T]):
    def __init__(
        self,
        result_handler: RawResultHandler[T],
        debug_file: Path | None,
        parse_scheme: Dict[str, Sequence[IndexedStringParserProtocol]] | None = None,
        ctx: dict[str, Any] | None = None,
    ) -> None:
        self.ctx = ctx
        if parse_scheme is None:
            self.parse_scheme = scheme()
        else:
            self.parse_scheme = parse_scheme

        self._result_handler = result_handler
        self.debug_file = debug_file
        self.debug_fp: None | TextIOWrapper = None

    def expected_parsers(
        self, state: str, **kwargs
    ) -> Sequence[IndexedStringParserProtocol]:
        _ = kwargs
        return self.parse_scheme[state]

    def result_handler(self) -> RawResultHandler[T]:
        return self._result_handler

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="w", encoding="utf-8")
            self.result_handler().debug_fp = self.debug_fp
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug_fp is not None:
            self.debug_fp.close()
