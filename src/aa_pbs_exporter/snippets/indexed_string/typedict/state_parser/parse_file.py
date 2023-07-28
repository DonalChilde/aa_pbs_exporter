from contextlib import nullcontext
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.indexed_string.typedict.index_strings import Indexer
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_job import (
    parse_job,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.result_handlers import (
    CollectResults,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
    IndexedStringParserProtocol,
    ResultHandlerProtocol,
)


def parse_text_file(
    file_in: Path,
    debug_file: Path | None,
    job_name: str,
    parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]],
    indexer: Callable[[Iterable[str]], Iterable[IndexedStringDict]] = Indexer(),
    ctx: dict[str, Any] | None = None,
    result_handler: ResultHandlerProtocol = CollectResults(),
    debug_out: bool = True,
) -> CollectedParseResults:
    if debug_file is None:
        debug_cm: nullcontext[None] | TextIOWrapper = nullcontext()
    else:
        validate_file_out(debug_file, overwrite=True)
        debug_cm = open(debug_file, mode="a", encoding="utf-8")
    with open(file_in, mode="rt", encoding="utf-8") as data, debug_cm as debug_fp:
        indexed_strings = indexer(data)
        result = parse_job(
            indexed_strings=indexed_strings,
            parser_lookup=parser_lookup,
            result_handler=result_handler,
            debug_out=debug_out,
            debug_fp=debug_fp,
            job_name=job_name,
            ctx=ctx,
        )
    return result
