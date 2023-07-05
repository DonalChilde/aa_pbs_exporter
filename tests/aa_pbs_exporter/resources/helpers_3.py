import logging
import traceback
from dataclasses import dataclass
from importlib import resources
from importlib.abc import Traversable
from typing import Callable, Iterable, Sequence

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
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
    parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]]
    indexer: Callable[[Iterable[str]], Iterable[IndexedString]]
