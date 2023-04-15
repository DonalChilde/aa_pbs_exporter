from typing import Any, Sequence

from aa_pbs_exporter.snippets.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseManagerProtocol,
    ParseResultProtocol,
    ParseSchemeProtocol,
    ResultHandlerProtocol,
)


class ParseManager(ParseManagerProtocol):
    def __init__(
        self,
        ctx: dict[str, Any],
        result_handler: ResultHandlerProtocol,
        parse_scheme: ParseSchemeProtocol,
    ) -> None:
        super().__init__()
        self.ctx = ctx
        self.result_handler = result_handler
        self.parse_scheme = parse_scheme

    def expected_parsers(
        self, current_state: str, **kwargs
    ) -> Sequence[IndexedStringParserProtocol]:
        return self.parse_scheme.expected_parsers(current_state=current_state)

    def handle_result(self, parse_result: ParseResultProtocol, **kwargs):
        self.result_handler.handle_result(parse_result=parse_result, **kwargs)
