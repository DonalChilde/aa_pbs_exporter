from importlib import resources
from logging import Logger
from pathlib import Path

from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_strings_td import index_pbs_strings
from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme_td import parser_lookup
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_file_to_json import (
    parse_file_to_json,
)
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData

SERIALIZE_ONLY = False
PDF_TEST_DATA = ResourceTestData(
    input_data="PBS_DCA_May_2022_20220408124308.txt", result_data=""
)
RAW_TEST_DATA = ResourceTestData("", "02MAY2022_DCA_raw.json")
COMPACT_TEST_DATA = ResourceTestData("", "2022-05-02_2022-06-01_DCA_compact.json")
EXPANDED_TEST_DATA = ResourceTestData("", "2022-05-02_2022-06-01_DCA_expanded.json")


# @pytest.mark.slow
# def test_txt(test_app_data_dir: Path, logger: Logger):
#     output_path = (
#         test_app_data_dir
#         / "txt_package"
#         / "dca_may_2022"
#         / __name__.rsplit(".", maxsplit=1)[-1]
#     )
#     res_dir = resources.files(__package__)
#     res_file = res_dir.joinpath(PDF_TEST_DATA.input_data)
#     raw_package, compact_package, expanded_package = parse_pbs_txt_file(
#         txt_file=res_file,
#         output_dir=output_path,
#     )
#     if not SERIALIZE_ONLY:
#         input_bytes = res_dir.joinpath(RAW_TEST_DATA.result_data).read_bytes()
#         raw_expected = parse_raw_as(raw.BidPackage, input_bytes)
#         assert raw_expected == raw_package
#         input_bytes = res_dir.joinpath(COMPACT_TEST_DATA.result_data).read_bytes()
#         compact_expected = parse_raw_as(compact.BidPackage, input_bytes)
#         assert compact_expected == compact_package
#         input_bytes = res_dir.joinpath(EXPANDED_TEST_DATA.result_data).read_bytes()
#         expanded_expected = parse_raw_as(expanded.BidPackage, input_bytes)
#         assert expanded_expected == expanded_package


def test_parse(test_app_data_dir: Path, logger: Logger):
    output_path = (
        test_app_data_dir
        / "txt_package"
        / "dca_may_2022"
        / __name__.rsplit(".", maxsplit=1)[-1]
    )
    res_dir = resources.files(__package__)
    res_file = res_dir.joinpath(PDF_TEST_DATA.input_data)
    json_path = output_path / f"{PDF_TEST_DATA.input_data}.json"
    debug_path = output_path / f"{PDF_TEST_DATA.input_data}_debug.txt"
    with resources.as_file(res_file) as file_in:
        result = parse_file_to_json(
            file_in=file_in,
            indexer=index_pbs_strings,
            parser_lookup=parser_lookup,
            file_out=json_path,
            debug_out=debug_path,
        )
    assert result is not None
    # assert False
