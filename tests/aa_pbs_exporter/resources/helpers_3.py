from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
)


@dataclass
class ParserTest:
    input_data: str
    result_data: str
    expected_data: str
    resource_package: str
    name: str
    category: str
    parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]]
    indexer: Callable[[Iterable[str]], Iterable[IndexedString]]
