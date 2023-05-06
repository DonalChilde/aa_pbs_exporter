import traceback
from hashlib import md5
from pathlib import Path
from typing import Callable, Iterable, Sequence

from aa_pbs_exporter.pbs_2022_01 import translate, validate
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
from aa_pbs_exporter.pbs_2022_01.parser import result_handlers
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.hash.file_hash import make_hashed_file
from aa_pbs_exporter.snippets.indexed_string.filters import (
    MultipleTests,
    SkipTillFirstMatch,
    not_white_space,
)
from aa_pbs_exporter.snippets.indexed_string.index_and_filter_strings import (
    index_and_filter_strings,
)
from aa_pbs_exporter.snippets.indexed_string.indexed_string_protocol import (
    IndexedStringProtocol,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_indexed_strings import (
    parse_indexed_strings,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.result_handler import (
    MultipleResultHandler,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseManagerProtocol,
    ResultHandlerProtocol,
)
from aa_pbs_exporter.snippets.messages.messenger import PrintMessenger
from aa_pbs_exporter.snippets.messages.publisher import Publisher

# TODO refactor helpers concept


def data_starts(indexed_string: IndexedStringProtocol) -> bool:
    if "DEPARTURE" in indexed_string.txt:
        return True
    return False


def pbs_data_filter() -> Callable[[IndexedStringProtocol], bool]:
    return MultipleTests(
        testers=[SkipTillFirstMatch(match_test=data_starts), not_white_space]
    )


def indexed_string_factory(idx: int, txt: str) -> IndexedStringProtocol:
    return raw.IndexedString(idx=idx, txt=txt)


def index_pbs_data(strings: Iterable[str]) -> Iterable[IndexedStringProtocol]:
    indexed_strings = index_and_filter_strings(
        strings=strings, string_filter=pbs_data_filter(), factory=indexed_string_factory
    )
    return indexed_strings


def parse_pbs_data(
    strings: Iterable[str],
    manager: ParseManagerProtocol,
    result_handler: ResultHandlerProtocol,
):
    indexed_strings = index_pbs_data(strings)
    result_handler.initialize(manager.ctx)
    for parse_result in parse_indexed_strings(
        indexed_strings=indexed_strings, manager=manager
    ):
        result_handler.handle_result(parse_result)
    result_handler.finalize(manager.ctx)


def parse_raw_bidpackage(
    strings: Iterable[str],
    source: HashedFile,
    manager: ParseManagerProtocol,
    validation_publisher: Publisher,
    additional_handlers: Sequence[ResultHandlerProtocol] | None = None,
) -> raw.BidPackage:
    # ensure_validation_publisher(manager)
    if additional_handlers is None:
        additional_handlers = []
    validator = validate.RawValidator(publisher=validation_publisher)
    translator = translate.ParsedToRaw(source=source, validator=validator)
    package_handler = result_handlers.RawResultHandler(translator=translator)
    handler = MultipleResultHandler(result_handlers=additional_handlers)
    handler.handlers.append(package_handler)

    parse_pbs_data(strings=strings, manager=manager, result_handler=handler)
    return package_handler.translator.bid_package


def debug_parse_raw_bidpackage(
    source_path: Path,
    manager: ParseManagerProtocol,
    debug_file_path: Path,
    additional_handlers: Sequence[ResultHandlerProtocol] | None = None,
) -> raw.BidPackage:
    # ensure_validation_publisher(manager)
    source = make_hashed_file(
        file_path=source_path, hasher=md5(), result_factory=HashedFile.factory
    )
    validate_file_out(debug_file_path)
    with open(debug_file_path, "w", encoding="utf-8") as debug_file:
        debug_file.write(f"source: {source}\n")
        debug_handler = result_handlers.DebugToFile(
            writer=debug_file, record_separator="\n"
        )
        validation_publisher = Publisher(consumers=[])
        debug_validation_messenger = PrintMessenger(file=debug_file)
        validation_publisher.consumers.append(debug_validation_messenger)
        handlers: list[ResultHandlerProtocol] = [debug_handler]
        if additional_handlers is not None:
            handlers.extend(additional_handlers)
        try:
            with open(source_path, encoding="utf-8") as file_in:
                result = parse_raw_bidpackage(
                    strings=file_in,
                    source=source,
                    manager=manager,
                    additional_handlers=handlers,
                    validation_publisher=validation_publisher,
                )
        except Exception as error:
            debug_file.write(str(error))
            traceback.print_exc(file=debug_file)
            raise error
        return result


# def ensure_validation_publisher(manager: ParseManagerProtocol):
#     publisher: Publisher = manager.ctx.get(
#         "validation_publisher", Publisher(messengers=[])
#     )
#     manager.ctx["validation_publisher"] = publisher
