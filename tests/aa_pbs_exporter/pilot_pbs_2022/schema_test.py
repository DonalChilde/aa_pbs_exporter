# # pylint: disable=missing-docstring
# import logging
# from io import StringIO
# from pathlib import Path
# from typing import Dict

# from pfmsoft.text_chunk_parser import AllFailedToParseException, ChunkIterator, Parser
# from pydantic.json import pydantic_encoder
# from tests.aa_pbs_exporter.conftest import FileResource

# from aa_pbs_exporter.models.bid_package import BidPackage
# from aa_pbs_exporter.pilot_pbs_2022.parser_2 import PbsResultHander, PbsSchema

# TEST_1 = """


#    DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/
# DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# BOS 737

# SEQ 23001   3 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0430/0430                                                          −− −− −−  5 −− −−  8
# 1  1/1 65 2265  BOS 0530/0530  B ORD 0724/0824   2.54          1.29X                    9 −− −− −− −− −− −−
# 1  1/1 65 1831  ORD 0853/0953  L PBI 1258/1258   3.05                                  −− −− −− −− −− −− −−
#                                  RLS 1313/1313   5.59   0.00   5.59   8.43        8.28 −− −− −− −− −− −− −−
#                 PBI MARRIOTT WEST PALM BEACH                15618331234    17.50       −− −− −−
#                     SHUTTLE
#                 RPT 0703/0703
# 2  2/2 45  550  PBI 0803/0803  B CLT 1000/1000   1.57          1.20X
# 2  2/2 45 1180  CLT 1120/1120  L BOS 1340/1340   2.20
#                                  RLS 1355/1355   4.17   0.00   4.17   6.52        6.37
# TTL                                             10.16   0.14  10.30        33.25
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 23002   2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0430/0430                                                          −− −− −− −−  6 −− −−
# 1  1/1 65 2265  BOS 0530/0530  B ORD 0724/0824   2.54          1.11X                   −− 10 −− −− −− −− −−
# 1  1/1 45 1652  ORD 0835/0935    PHL 1137/1137   2.02                                  −− −− −− −− −− −− −−
#                                  RLS 1152/1152   4.56   0.00   4.56   7.22        7.07 −− −− −− −− −− −− −−
#                 PHL MARRIOTT OLD CITY                       12152386000    17.08       −− −− −−
#                     SKYHOP GLOBAL                           9544000412
#                 RPT 0500/0500
# 2  2/2 45  551  PHL 0600/0600  B MIA 0857/0857   2.57          1.53X
# 2  2/2 45  845  MIA 1050/1050  L BOS 1417/1417   3.27
#                                  RLS 1432/1432   6.24   0.00   6.24   9.32        9.17
# TTL                                             11.20   0.00  11.20        34.02
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 23003   2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0430/0430                                                          −− −− −− −− −− −− −−
# 1  1/1 65 2265  BOS 0530/0530  B ORD 0724/0824   2.54          1.29X                   −− −− −− −− 13 −− −−
# 1  1/1 65 1831  ORD 0853/0953  L PBI 1258/1258   3.05                                  −− −− 18 −− −− −− −−
#                                  RLS 1313/1313   5.59   0.00   5.59   8.43        8.28 −− −− −− −− −− −− −−
#                 PBI MARRIOTT WEST PALM BEACH                15618331234    17.50       −− −− −−
#                     SHUTTLE
#                 RPT 0703/0703
# 2  2/2 45  550  PBI 0803/0803  B CLT 1000/1000   1.57          1.30X
# 2  2/2 45 1662  CLT 1130/1130  L DEN 1310/1510   3.40
#                                  RLS 1325/1525   5.37   0.00   5.37   8.22        8.07
#                 DEN CAMBRIA SUITES                          13035769600    15.22
#                     SHUTTLE
#                 RPT 0447/0647
# 3  3/3 45 2771  DEN 0547/0747  B ORD 0915/1015   2.28          1.00
# 3  3/3 45 1194  ORD 1015/1115    BOS 1337/1337   2.22
#                                  RLS 1352/1352   4.50   0.00   4.50   7.05        6.50
# TTL                                             16.26   0.00  16.26        57.22
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 23004   2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0430/0430                                                          −− −− −− −− −− −− −−
# 1  1/1 65 2265  BOS 0530/0530  B ORD 0724/0824   2.54          1.29X                   −− −− −− −− −− −− −−
# 1  1/1 65 1831  ORD 0853/0953  L PBI 1258/1258   3.05                                  −− −− −− −− −− −− −−
#                                  RLS 1313/1313   5.59   0.00   5.59   8.43        8.28 −− 24 −− 26 −− −− −−
#                 PBI MARRIOTT WEST PALM BEACH                15618331234    17.50       −− −− −−
#                     SHUTTLE
#                 RPT 0703/0703
# 2  2/2 45  550  PBI 0803/0803  B CLT 1000/1000   1.57          1.20X
# 2  2/2 45 1180  CLT 1120/1120  L BOS 1340/1340   2.20
#                                  RLS 1355/1355   4.17   0.00   4.17   6.52        6.37
# TTL                                             10.16   0.14  10.30        33.25
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−

# COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               BOS 737  DOM                              PAGE     1

# """


# # def schema_test(
# #     logger: logging.Logger,
# #     handler: PbsResultHander,
# #     chunk_iterator: ChunkIterator,
# #     test_name: str,
# # ) -> BidPackage:
# #     schema = PbsSchema()
# #     parser = Parser(schema, log_on_success=False)
# #     logging.info("Begining schema test with source: %s", test_name)
# #     try:
# #         parser.parse(handler, chunk_iterator)
# #     except AllFailedToParseException as exc:
# #         logger.exception(exc)
# #         assert False


# def test_first_page(logger: logging.Logger, caplog):
#     caplog.set_level(logging.INFO)
#     schema = PbsSchema()
#     parser = Parser(schema, log_on_success=True)
#     source_text = StringIO(TEST_1)
#     chunk_iterator = ChunkIterator(source_text, "First Page Test")
#     with PbsResultHander(year=2022) as handler:
#         try:
#             parser.parse(handler, chunk_iterator)
#             bid_package = handler.bid_package
#         except AllFailedToParseException as exc:
#             logger.warning(exc)
#     assert bid_package.base == {"BOS"}


# def parse_file(file_path: Path, year: int) -> BidPackage:
#     schema = PbsSchema()
#     parser = Parser(schema, log_on_success=True)
#     with (
#         PbsResultHander(year=year) as handler,
#         open(file_path, "rt", encoding="utf-8") as file,
#     ):
#         chunk_iterator = ChunkIterator(file, source=str(file_path))
#         parser.parse(handler, chunk_iterator)
#         return handler.bid_package


# def test_file(logger: logging.Logger, pairing_text_files: Dict[str, FileResource]):
#     resource_name = "PBS_BOS_May_2022_20220408124104.txt"
#     file_path = pairing_text_files[resource_name].file_path
#     try:
#         bid_package = parse_file(file_path, 2022)
#     except AllFailedToParseException as exc:
#         logger.warning(exc)
#     assert bid_package.base == {"BOS"}
#     # print(context.package)


# def test_all_files(
#     capsys, logger: logging.Logger, pairing_text_files: Dict[str, FileResource]
# ):
#     for resource_name, resource in pairing_text_files.items():
#         file_path = resource.file_path
#         with capsys.disabled():
#             print(f"Beginning test of {resource_name}")
#         try:
#             bid_package = parse_file(file_path, 2022)
#             assert bid_package.base
#         except AllFailedToParseException as exc:
#             logger.warning(exc)
#             assert False


# def test_file_serialize_pydantic(
#     logger: logging.Logger,
#     pairing_text_files: Dict[str, FileResource],
#     test_app_data_dir: Path,
# ):
#     resource_name = "PBS_BOS_May_2022_20220408124104.txt"
#     file_path = pairing_text_files[resource_name].file_path
#     try:
#         bid_package = parse_file(file_path, 2022)
#     except AllFailedToParseException as exc:
#         logger.warning(exc)
#     # print(context.package)

#     assert bid_package.base == set(["BOS"])
#     file_path = test_app_data_dir / "boston.json"
#     file_path.write_text(bid_package.json(indent=2))
#     print(bid_package.bid_sequences[-1].duty_periods[-1].flights[-1].json(indent=2))
#     assert False
