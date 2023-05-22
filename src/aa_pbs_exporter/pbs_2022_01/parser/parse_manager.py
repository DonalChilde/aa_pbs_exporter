from typing import Any, Dict, Generic, Sequence, TypeVar

from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme import parse_scheme as scheme
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ResultHandlerProtocol,
)

T = TypeVar("T")


class ParseManager(Generic[T]):
    def __init__(
        self,
        result_handler: ResultHandlerProtocol[T],
        parse_scheme: Dict[str, Sequence[IndexedStringParserProtocol]] | None = None,
        ctx: dict[str, Any] | None = None,
    ) -> None:
        self.ctx = ctx
        if parse_scheme is None:
            self.parse_scheme = scheme()
        else:
            self.parse_scheme = parse_scheme

        self._result_handler = result_handler

    def expected_parsers(
        self, state: str, **kwargs
    ) -> Sequence[IndexedStringParserProtocol]:
        _ = kwargs
        return self.parse_scheme[state]

    def result_handler(self) -> ResultHandlerProtocol[T]:
        return self._result_handler
