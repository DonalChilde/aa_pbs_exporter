import logging
import traceback
from pathlib import Path
from time import perf_counter_ns
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel

from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
NANOS_PER_SECOND = 1000000000
T = TypeVar("T", bound=BaseModel)


# TODO make snippet
def nanos_to_seconds(start: int, end: int) -> float:
    return (end - start) / NANOS_PER_SECOND


class SerializePydantic(Generic[T]):
    """A basic Pydantic to/from json serializer with perf logging."""

    def __init__(self) -> None:
        super().__init__()

    def save_as_json(
        self,
        file_out: Path,
        data: T,
        overwrite: bool = False,
        indent: int = 2,
        **kwargs,
    ):
        kwargs["indent"] = indent
        start = perf_counter_ns()
        validate_file_out(file_out, overwrite=overwrite)
        file_out.write_text(data.json(**kwargs))
        end = perf_counter_ns()
        logger.info(
            "Saved %s to %s in %s seconds.\n\tCalled From:\n\t%s",
            data.__class__.__name__,
            file_out,
            nanos_to_seconds(start, end),
            traceback.format_stack()[-2],
        )

    def load_from_json_file(self, model: Any, file_in: Path, **kwargs) -> T:
        start = perf_counter_ns()
        results = model.parse_file(file_in, **kwargs)
        end = perf_counter_ns()
        logger.info(
            "Loaded %s from %s in %s seconds.\n\tCalled From:\n\t%s",
            model.__class__.__name__,
            file_in,
            nanos_to_seconds(start, end),
            traceback.format_stack()[-2],
        )
        return results
