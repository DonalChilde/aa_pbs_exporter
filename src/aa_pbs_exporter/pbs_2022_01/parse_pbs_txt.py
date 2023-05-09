# from hashlib import md5
# from pathlib import Path

# from aa_pbs_exporter.pbs_2022_01.helpers.helpers import parse_raw_bidpackage
# from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
# from aa_pbs_exporter.pbs_2022_01.parser.parse_manager import ParseManager
# from aa_pbs_exporter.snippets.hash.file_hash import make_hashed_file


# def parse_pbs_txt(
#     txt_file: Path,
#     output_dir: Path,
#     debug: bool = False,
#     include_source: bool = True,
#     rename_source: bool = True,
# ):
#     debug_path = output_dir / txt_file.name
#     debug_path = debug_path.with_suffix(".debug.txt")
#     source = make_hashed_file(
#         file_path=txt_file, hasher=md5(), result_factory=HashedFile.factory
#     )
#     manager = ParseManager()
#     try:
#         with open(txt_file, encoding="utf-8") as file_in:
#             result = parse_raw_bidpackage(
#                 strings=file_in,
#                 source=source,
#                 manager=manager,
#                 additional_handlers=handlers,
#                 validation_publisher=validation_publisher,
#             )
#     except Exception as error:
#         debug_file.write(str(error))
#         traceback.print_exc(file=debug_file)
#         raise error
#     return result


# def parse_no_debug():
#     pass


# def parse_with_debug():
#     pass
