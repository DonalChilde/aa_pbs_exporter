import json
from pathlib import Path

from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
)


def save_as_json(
    file_out: Path,
    parse_results: CollectedParseResults,
    overwrite: bool = False,
    indent: int = 2,
):
    validate_file_out(file_out, overwrite=overwrite)
    with open(file_out, mode="w", encoding="utf-8") as file_fp:
        json.dump(parse_results, fp=file_fp, indent=indent)


def load_from_json(file_in: Path) -> CollectedParseResults:
    with open(file_in, mode="rb") as file_fp:
        results = json.load(file_fp)
    return results
