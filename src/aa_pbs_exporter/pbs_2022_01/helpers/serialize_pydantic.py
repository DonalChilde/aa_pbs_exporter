import logging
import traceback
from pathlib import Path
from time import perf_counter_ns
from typing import Any, Generic, TypeVar

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

    def save_json(
        self,
        file_out: Path,
        data: T,
        overwrite: bool = False,
        indent: int | None = 2,
        **kwargs,
    ):
        kwargs["indent"] = indent
        start = perf_counter_ns()
        validate_file_out(file_out, overwrite=overwrite)
        data.model_dump_json(**kwargs)
        file_out.write_text(data.model_dump_json(**kwargs))
        end = perf_counter_ns()
        logger.info(
            "Saved %s to %s in %s seconds.\n\tCalled From:\n\t%s",
            data.__class__.__name__,
            file_out,
            nanos_to_seconds(start, end),
            traceback.format_stack()[-2],
        )

    def load_json(
        self,
        model: T,
        file_in: Path,
        strict: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> T:
        start = perf_counter_ns()
        with open(file=file_in, mode="rb") as file_fp:
            results = model.model_validate_json(
                file_fp.read(), strict=strict, context=context
            )
        end = perf_counter_ns()
        logger.info(
            "Loaded %s from %s in %s seconds.\n\tCalled From:\n\t%s",
            model.__class__.__name__,
            file_in,
            nanos_to_seconds(start, end),
            traceback.format_stack()[-2],
        )
        return results
