import logging
import traceback
from dataclasses import dataclass, field
from hashlib import md5
from importlib import resources
from importlib.abc import Traversable
from typing import Callable, Iterable, Sequence

from aa_pbs_exporter.snippets.hash.file_hash import (
    HashedFileDict,
    make_hashed_file_dict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseResult,
)

logger = logging.getLogger(__name__)


# TODO add this to snippets
@dataclass
class ResourceLocator:
    package: str
    file: str

    def file_resource(self) -> Traversable:
        package_resource = resources.files(self.package)
        logger.info(
            "Finding Resource %s\n\tCalled From:\n\t%s",
            str(self),
            traceback.format_stack()[-2],
        )
        return package_resource.joinpath(self.file)

    def __str__(self) -> str:
        return f"{self.package}.{self.file}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"package={self.package}, "
            f"file={self.file!r})"
        )


@dataclass
class ParserTest:
    input_data: ResourceLocator
    result_data: str
    expected_data: ResourceLocator
    name: str
    category: str
    # parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]]
    # indexer: Callable[[Iterable[str]], Iterable[IndexedStringDict]]


def hashed_file_from_resource(
    file_resource: ResourceLocator, resource_as_path: bool = True
) -> HashedFileDict:
    with resources.as_file(file_resource.file_resource()) as file_path:
        hashed_file = make_hashed_file_dict(file_path=file_path, hasher=md5())
    if resource_as_path:
        hashed_file["file_path"] = str(file_resource)
    return hashed_file


@dataclass
class GrammarTest:
    txt: str
    description: str = ""
    result: dict = field(default_factory=dict)


@dataclass
class ParserTest2:
    idx_str: IndexedStringDict
    result: ParseResult
    description: str = ""
