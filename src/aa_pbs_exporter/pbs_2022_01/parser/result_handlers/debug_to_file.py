from aa_pbs_exporter.snippets.indexed_string.state_parser.result_handler import (
    ParseResultToFile,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseResultProtocol,
)


class DebugToFile(ParseResultToFile):
    def result_to_txt(
        self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
    ) -> str:
        return f"{parse_result}"
