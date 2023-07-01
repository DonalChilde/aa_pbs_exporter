from importlib import resources
from logging import Logger
from pathlib import Path

import pytest
from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_strings_td import index_pbs_strings

from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme_td import parser_lookup
from aa_pbs_exporter.snippets.indexed_string.typedict.index_strings import index_strings
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser import serialize
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseException,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_file_to_json import (
    parse_file_to_json,
)
from tests.aa_pbs_exporter.resources.helpers_3 import ParserTest

SERIALIZE_ONLY = False

PAGE_TEST_DATA = [
    ParserTest(
        input_data="20220408124308.txt",
        result_data="20220408124308.json",
        expected_data="20220408124308.json",
        resource_package=f"{__package__}.resources",
        name="PBS_DCA_May_2022",
        category="full_package",
        parser_lookup=parser_lookup,
        indexer=index_pbs_strings,
    ),
    ParserTest(
        input_data="20220408124407.txt",
        result_data="20220408124407.json",
        expected_data="20220408124407.json",
        resource_package=f"{__package__}.resources",
        name="PBS_DFW_May_2022",
        category="full_package",
        parser_lookup=parser_lookup,
        indexer=index_pbs_strings,
    ),
]
PAGE_FAIL_TEST_DATA = [
    ParserTest(
        input_data="20220408124308.txt",
        result_data="20220408124308.json",
        expected_data="20220408124308.json",
        resource_package=f"{__package__}.resources",
        name="PBS_DCA_May_2022",
        category="full_package",
        parser_lookup=parser_lookup,
        indexer=index_strings,
    ),
]


@pytest.mark.slow
@pytest.mark.parametrize("test_data", PAGE_TEST_DATA)
def test_parser(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category
    res_dir = resources.files(f"{test_data.resource_package}.{test_data.category}")
    res_file = res_dir.joinpath(f"{test_data.name}_{test_data.input_data}")
    json_path = output_path / f"{test_data.name}_{test_data.result_data}"
    debug_path = output_path / f"{test_data.name}_{test_data.input_data}_debug.txt"
    with resources.as_file(res_file) as file_in:
        result = parse_file_to_json(
            file_in=file_in,
            indexer=test_data.indexer,
            parser_lookup=test_data.parser_lookup,
            file_out=json_path,
            debug_out=debug_path,
        )
    if not SERIALIZE_ONLY:
        expected_res = res_dir.joinpath(f"{test_data.name}_{test_data.result_data}")
        with resources.as_file(expected_res) as expected_file:
            expected = serialize.load_from_json(file_in=expected_file)
        assert result == expected


@pytest.mark.parametrize("test_data", PAGE_FAIL_TEST_DATA)
def test_parser_fail(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category / "fail"
    res_dir = resources.files(f"{test_data.resource_package}.{test_data.category}")
    res_file = res_dir.joinpath(f"{test_data.name}_{test_data.input_data}")
    json_path = output_path / f"{test_data.name}_{test_data.result_data}"
    debug_path = output_path / f"{test_data.name}_{test_data.input_data}_debug.txt"
    with resources.as_file(res_file) as file_in:
        with pytest.raises(ParseException):
            result = parse_file_to_json(
                file_in=file_in,
                indexer=test_data.indexer,
                parser_lookup=test_data.parser_lookup,
                file_out=json_path,
                debug_out=debug_path,
            )
