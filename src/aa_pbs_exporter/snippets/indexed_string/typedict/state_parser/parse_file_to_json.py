from pathlib import Path
from typing import Callable, Iterable, Sequence
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_job import (
    parse_job,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.result_handlers import (
    SaveAsJson,
)

from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    CollectedParseResults,
)


def parse_file_to_json(
    file_in: Path,
    parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]],
    indexer: Callable[[Iterable[str]], Iterable[IndexedString]],
    file_out: Path | None = None,
    debug_out: Path | None = None,
    **kwargs,
) -> CollectedParseResults | None:
    result: CollectedParseResults | None = None
    with open(file_in, encoding="utf-8") as txt_file:
        indexed_strings = indexer(txt_file)
        result_handler = SaveAsJson(
            file_out=file_out,
            debug_out=debug_out,
            **kwargs,
        )
        result = parse_job(
            indexed_strings=indexed_strings,
            parser_lookup=parser_lookup,
            result_handler=result_handler,
            ctx={},
        )
    return result
