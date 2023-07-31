from importlib import resources
from logging import Logger
from pathlib import Path

import pytest

from aa_pbs_exporter.pbs_2022_01.api import (
    load_parse_results,
    parse_pbs_txt_file,
    save_parse_results,
)
from tests.aa_pbs_exporter.resources import RESOURCE_PATH
from tests.aa_pbs_exporter.resources.helpers_3 import (
    ResourceLocator,
    hashed_file_from_resource,
)

SERIALIZE_ONLY = False


@pytest.mark.slow
def test_small_package(test_app_data_dir: Path, logger: Logger):
    category = "bid_package"
    file_stem = "PBS_DCA_May_2022_20220408124308"
    job_name = "PBS_DCA_May_2022"

    output_path = test_app_data_dir / category
    json_path = output_path / f"{file_stem}-parsed.json"
    debug_path = output_path / f"{file_stem}.parsed-debug.txt"
    input_resource = ResourceLocator(f"{RESOURCE_PATH}.{category}", f"{file_stem}.txt")
    expected_resource = ResourceLocator(
        f"{RESOURCE_PATH}.{category}", f"{file_stem}-parsed.json"
    )
    hashed_file = hashed_file_from_resource(input_resource)
    with resources.as_file(input_resource.file_resource()) as file_in:
        result = parse_pbs_txt_file(
            file_in=file_in,
            debug_file=debug_path,
            job_name=job_name,
            metadata={"source": hashed_file},
        )
        save_parse_results(file_out=json_path, parse_results=result)
    if not SERIALIZE_ONLY:
        with resources.as_file(expected_resource.file_resource()) as expected_file:
            expected = load_parse_results(file_in=expected_file)
        assert result == expected
        # assert False


@pytest.mark.slow
def test_large_package(test_app_data_dir: Path, logger: Logger):
    category = "bid_package"
    file_stem = "PBS_DFW_May_2022_20220408124407"
    job_name = "PBS_DFW_May_2022"

    output_path = test_app_data_dir / category
    json_path = output_path / f"{file_stem}-parsed.json"
    debug_path = output_path / f"{file_stem}.parsed-debug.txt"
    input_resource = ResourceLocator(f"{RESOURCE_PATH}.{category}", f"{file_stem}.txt")
    expected_resource = ResourceLocator(
        f"{RESOURCE_PATH}.{category}", f"{file_stem}-parsed.json"
    )
    hashed_file = hashed_file_from_resource(input_resource)
    with resources.as_file(input_resource.file_resource()) as file_in:
        result = parse_pbs_txt_file(
            file_in=file_in,
            debug_file=debug_path,
            job_name=job_name,
            metadata={"source": hashed_file},
        )
        save_parse_results(file_out=json_path, parse_results=result)
    if not SERIALIZE_ONLY:
        with resources.as_file(expected_resource.file_resource()) as expected_file:
            expected = load_parse_results(file_in=expected_file)
        assert result == expected
        # assert False


# # @pytest.mark.slow
# @pytest.mark.parametrize("test_data", PACKAGE_TEST_DATA)
# def test_parser(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
#     output_path = test_app_data_dir / test_data.category
#     json_path = output_path / f"{test_data.expected_data.file}"
#     debug_path = output_path / f"{test_data.expected_data.file}_debug.txt"
#     hashed_file = hashed_file_from_resource(test_data.input_data)
#     with resources.as_file(test_data.input_data.file_resource()) as file_in:
#         result = parse_pbs_txt_file(
#             file_in=file_in,
#             debug_file=debug_path,
#             job_name=test_data.name,
#             metadata={"source": hashed_file},
#         )
#         save_parse_results(file_out=json_path, parse_results=result)
#     if not SERIALIZE_ONLY:
#         with resources.as_file(
#             test_data.expected_data.file_resource()
#         ) as expected_file:
#             expected = serialize.load_from_json(file_in=expected_file)
#         assert result == expected
#         # assert False


# @pytest.mark.parametrize("test_data", PACKAGE_FAIL_TEST_DATA)
# def test_parser_fail(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
#     output_path = test_app_data_dir / test_data.category / "fail"
#     # json_path = output_path / f"{test_data.expected_data.file}"
#     debug_path = output_path / f"{test_data.expected_data.file}_debug.txt"
#     with resources.as_file(test_data.input_data.file_resource()) as file_in:
#         with pytest.raises(ParseException):
#             result = parse_pbs_txt_file(
#                 file_in=file_in,
#                 debug_file=debug_path,
#                 job_name=test_data.name,
#                 metadata={},
#             )
#             _ = result
