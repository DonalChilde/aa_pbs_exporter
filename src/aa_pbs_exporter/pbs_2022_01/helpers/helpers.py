# import traceback
# from hashlib import md5
# from pathlib import Path
# from typing import Iterable

# from aa_pbs_exporter.pbs_2022_01 import translate, validate
# from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_data import parse_pbs_data
# from aa_pbs_exporter.pbs_2022_01.models import raw
# from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
# from aa_pbs_exporter.pbs_2022_01.parser import result_handlers
# from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
# from aa_pbs_exporter.snippets.hash.file_hash import make_hashed_file

# from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
#     ParseManagerProtocol,
# )
# from aa_pbs_exporter.snippets.messages.messenger import PrintMessenger
# from aa_pbs_exporter.snippets.messages.publisher import Publisher


# def parse_raw_bidpackage(
#     strings: Iterable[str],
#     source: HashedFile,
#     manager: ParseManagerProtocol,
#     validation_publisher: Publisher,
#     # additional_handlers: Sequence[ResultHandlerProtocol] | None = None,
# ) -> raw.BidPackage | None:
#     # ensure_validation_publisher(manager)
#     # if additional_handlers is None:
#     #     additional_handlers = []
#     validator = validate.RawValidator(msg_bus=validation_publisher)
#     translator = translate.ParsedToRaw(source=source, validator=validator)
#     package_handler = result_handlers.RawResultHandler(translator=translator)
#     # handler = MultipleResultHandler(result_handlers=additional_handlers)
#     # handler.handlers.append(package_handler)

#     parse_pbs_data(strings=strings, manager=manager, result_handler=package_handler)
#     return package_handler.result_data()


# def debug_parse_raw_bidpackage(
#     source_path: Path,
#     manager: ParseManagerProtocol,
#     debug_file_path: Path,
#     # additional_handlers: Sequence[ResultHandlerProtocol] | None = None,
# ) -> raw.BidPackage | None:
#     # ensure_validation_publisher(manager)
#     source = make_hashed_file(
#         file_path=source_path, hasher=md5(), result_factory=HashedFile.factory
#     )
#     validate_file_out(debug_file_path)
#     with open(debug_file_path, "w", encoding="utf-8") as debug_file:
#         debug_file.write(f"source: {source}\n")
#         debug_handler = result_handlers.DebugToFile(
#             writer=debug_file, record_separator="\n"
#         )
#         validation_publisher = Publisher(consumers=[])
#         debug_validation_messenger = PrintMessenger(file=debug_file)
#         validation_publisher.consumers.append(debug_validation_messenger)
#         # handlers: list[ResultHandlerProtocol] = [debug_handler]
#         # if additional_handlers is not None:
#         #     handlers.extend(additional_handlers)
#         try:
#             with open(source_path, encoding="utf-8") as file_in:
#                 result = parse_raw_bidpackage(
#                     strings=file_in,
#                     source=source,
#                     manager=manager,
#                     # additional_handlers=handlers,
#                     validation_publisher=validation_publisher,
#                 )
#         except Exception as error:
#             debug_file.write(str(error))
#             traceback.print_exc(file=debug_file)
#             raise error
#         return result


# # def ensure_validation_publisher(manager: ParseManagerProtocol):
# #     publisher: Publisher = manager.ctx.get(
# #         "validation_publisher", Publisher(messengers=[])
# #     )
# #     manager.ctx["validation_publisher"] = publisher
