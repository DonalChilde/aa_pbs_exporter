import json
import logging
from pathlib import Path
from time import perf_counter_ns

from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
NANOS_PER_SECOND = 1000000000


# TODO make snippet
def nanos_to_seconds(start: int, end: int) -> float:
    return (end - start) / NANOS_PER_SECOND


def save_as_json(
    file_out: Path,
    parse_results: CollectedParseResults,
    overwrite: bool = False,
    indent: int = 2,
):
    start = perf_counter_ns()
    validate_file_out(file_out, overwrite=overwrite)
    with open(file_out, mode="w", encoding="utf-8") as file_fp:
        json.dump(parse_results, fp=file_fp, indent=indent)
    end = perf_counter_ns()
    logger.info(
        "Saved CollectedParseResults to %s in %s seconds",
        file_out,
        nanos_to_seconds(start, end),
    )


def load_from_json(file_in: Path) -> CollectedParseResults:
    start = perf_counter_ns()
    with open(file_in, mode="rb") as file_fp:
        results = json.load(file_fp)
    end = perf_counter_ns()
    logger.info(
        "Loaded CollectedParseResults from %s in %s seconds",
        file_in,
        nanos_to_seconds(start, end),
    )
    return results
