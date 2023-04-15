from pathlib import Path
from typing import Callable, Iterable

from aa_pbs_exporter.snippets.file.line_reader import line_reader
from aa_pbs_exporter.snippets.state_parser.parsed_indexed_strings import (
    parsed_indexed_strings,
)
from aa_pbs_exporter.snippets.state_parser.state_parser_protocols import (
    ParseManagerProtocol,
    ParseResultProtocol,
)
from aa_pbs_exporter.snippets.string.filtered_indexed_strings import (
    filtered_indexed_strings,
)
from aa_pbs_exporter.snippets.string.indexed_string_protocol import (
    IndexedStringProtocol,
)


def parse_file(
    file_path: Path,
    manager: ParseManagerProtocol,
    string_filter: Callable[[IndexedStringProtocol], bool],
    factory: Callable[[int, str], IndexedStringProtocol],
) -> Iterable[ParseResultProtocol]:
    input_file = line_reader(file_path)
    indexed_strings = filtered_indexed_strings(
        input_file, string_filter=string_filter, factory=factory
    )
    for parse_result in parsed_indexed_strings(
        indexed_strings=indexed_strings, manager=manager
    ):
        yield parse_result
