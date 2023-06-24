from datetime import UTC, datetime
from hashlib import md5
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Dict, Generic, Self, Sequence, TypeVar

from aa_pbs_exporter.pbs_2022_01 import translate, validate
from aa_pbs_exporter.pbs_2022_01.helpers.file_safe_date import file_safe_date
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme import parse_scheme as scheme
from aa_pbs_exporter.pbs_2022_01.parser.result_handlers import RawResultHandler
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.hash.file_hash import make_hashed_file
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
)

T = TypeVar("T")


class ParseManager(Generic[T]):
    def __init__(
        self,
        result_handler: RawResultHandler[T],
        debug_file: Path | None,
        parse_scheme: Dict[str, Sequence[IndexedStringParserProtocol]] | None = None,
        ctx: dict[str, Any] | None = None,
    ) -> None:
        self.ctx = ctx
        if parse_scheme is None:
            self.parse_scheme = scheme()
        else:
            self.parse_scheme = parse_scheme

        self._result_handler = result_handler
        self.debug_file = debug_file
        self.debug_fp: None | TextIOWrapper = None

    def expected_parsers(
        self, state: str, **kwargs
    ) -> Sequence[IndexedStringParserProtocol]:
        _ = kwargs
        return self.parse_scheme[state]

    def result_handler(self) -> RawResultHandler[T]:
        return self._result_handler

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="w", encoding="utf-8")
            self.result_handler().debug_fp = self.debug_fp
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug_fp is not None:
            self.debug_fp.close()


def file_parse_manager(
    source_path: Path, debug_dir: Path | None = None
) -> ParseManager[raw.BidPackage]:
    source_hash = make_hashed_file(
        file_path=source_path, hasher=md5(), result_factory=HashedFile.factory
    )
    if debug_dir is not None:
        debug_file = file_debug_path(debug_dir=debug_dir, source_hash=source_hash)
    else:
        debug_file = None
    return config_parse_manager(source_hash=source_hash, debug_file=debug_file)


def config_parse_manager(
    source_hash: HashedFile | None, debug_file: Path | None
) -> ParseManager[raw.BidPackage]:
    validator = validate.RawValidator()
    translator = translate.ParsedToRaw(
        source=source_hash,
        validator=validator,
    )
    result_handler: RawResultHandler = RawResultHandler[raw.BidPackage](
        translator=translator,
    )
    manager: ParseManager[raw.BidPackage] = ParseManager(
        result_handler=result_handler, debug_file=debug_file
    )
    return manager


def string_parse_manager(
    job_name: str,
    debug_dir: Path | None = None,
):
    if debug_dir is not None:
        debug_file = string_debug_path(debug_dir=debug_dir, name=job_name)
    else:
        debug_file = None
    return config_parse_manager(source_hash=None, debug_file=debug_file)


def file_debug_path(debug_dir: Path, source_hash: HashedFile) -> Path:
    debug_path = (
        debug_dir
        / f"{source_hash.file_path.name}_{source_hash.file_hash}_parse-debug.txt"
    )
    return debug_path


def string_debug_path(
    debug_dir: Path,
    name: str,
) -> Path:
    now_utc = datetime.now(UTC)
    debug_path = debug_dir / f"{name}_{file_safe_date(now_utc)}_parse-debug.txt"
    return debug_path
