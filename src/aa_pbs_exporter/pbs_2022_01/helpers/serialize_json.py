import json
import logging
from pathlib import Path
from time import perf_counter_ns
from typing import Generic, TypeVar
import traceback
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
NANOS_PER_SECOND = 1000000000
T = TypeVar("T")


# TODO make snippet
def nanos_to_seconds(start: int, end: int) -> float:
    return (end - start) / NANOS_PER_SECOND


class SerializeJson(Generic[T]):
    """A basic to/from json serializer with perf logging."""

    def __init__(self, data_type_name: str = "data") -> None:
        super().__init__()
        self.data_type_name = data_type_name

    def save_json(
        self,
        file_out: Path,
        data: T,
        overwrite: bool = False,
        indent: int = 2,
    ):
        start = perf_counter_ns()
        validate_file_out(file_out, overwrite=overwrite)
        with open(file_out, mode="w", encoding="utf-8") as file_fp:
            json.dump(data, fp=file_fp, indent=indent)
        end = perf_counter_ns()
        logger.info(
            "Saved %s to %s in %s seconds.\n\tCalled From:\n\t%s",
            self.data_type_name,
            file_out,
            nanos_to_seconds(start, end),
            traceback.format_stack()[-2],
        )

    def load_json(self, file_in: Path) -> T:
        start = perf_counter_ns()
        with open(file_in, mode="rb") as file_fp:
            results = json.load(file_fp)
        end = perf_counter_ns()
        logger.info(
            "Loaded %s from %s in %s seconds.\n\tCalled From:\n\t%s",
            self.data_type_name,
            file_in,
            nanos_to_seconds(start, end),
            traceback.format_stack()[-2],
        )
        return results
