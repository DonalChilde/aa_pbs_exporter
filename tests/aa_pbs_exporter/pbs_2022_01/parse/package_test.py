from importlib import resources
from logging import Logger
from pathlib import Path

import pytest
from aa_pbs_exporter.pbs_2022_01.api import parse_pbs_txt_file, save_parse_results

from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme import parser_lookup
from aa_pbs_exporter.snippets.indexed_string.typedict.index_strings import index_strings
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser import serialize
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseException,
)

from tests.aa_pbs_exporter.resources.helpers_3 import (
    ParserTest,
    ResourceLocator,
    hashed_file_from_resource,
)

SERIALIZE_ONLY = False
RESOURCE_DIR = f"{__package__}.resources.full_package"

PACKAGE_TEST_DATA = [
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "PBS_DCA_May_2022_20220408124308.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "PBS_DCA_May_2022_20220408124308.json"
        ),
        name="PBS_DCA_May_2022",
        category="full_package",
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "PBS_DFW_May_2022_20220408124407.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "PBS_DFW_May_2022_20220408124407.json"
        ),
        name="PBS_DFW_May_2022",
        category="full_package",
    ),
]
PACKAGE_FAIL_TEST_DATA = [
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "fail.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "PBS_DCA_May_2022_20220408124308.json"
        ),
        name="PBS_DCA_May_2022",
        category="full_package",
    ),
]


@pytest.mark.slow
@pytest.mark.parametrize("test_data", PACKAGE_TEST_DATA)
def test_parser(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category
    json_path = output_path / f"{test_data.expected_data.file}"
    debug_path = output_path / f"{test_data.expected_data.file}_debug.txt"
    hashed_file = hashed_file_from_resource(test_data.input_data)
    with resources.as_file(test_data.input_data.file_resource()) as file_in:
        result = parse_pbs_txt_file(
            file_in=file_in,
            debug_file=debug_path,
            job_name=test_data.name,
            metadata={"source": hashed_file},
        )
        save_parse_results(file_out=json_path, parse_results=result)
    if not SERIALIZE_ONLY:
        with resources.as_file(
            test_data.expected_data.file_resource()
        ) as expected_file:
            expected = serialize.load_from_json(file_in=expected_file)
        assert result == expected
        # assert False


@pytest.mark.parametrize("test_data", PACKAGE_FAIL_TEST_DATA)
def test_parser_fail(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category / "fail"
    # json_path = output_path / f"{test_data.expected_data.file}"
    debug_path = output_path / f"{test_data.expected_data.file}_debug.txt"
    with resources.as_file(test_data.input_data.file_resource()) as file_in:
        with pytest.raises(ParseException):
            result = parse_pbs_txt_file(
                file_in=file_in,
                debug_file=debug_path,
                job_name=test_data.name,
                metadata={},
            )
            _ = result
