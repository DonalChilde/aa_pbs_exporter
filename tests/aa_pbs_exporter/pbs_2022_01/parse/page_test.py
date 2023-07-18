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
from tests.aa_pbs_exporter.resources.helpers_3 import (
    ParserTest,
    ResourceLocator,
    hashed_file_from_resource,
)

SERIALIZE_ONLY = False
RESOURCE_DIR = f"{__package__}.resources.page"

PAGE_TEST_DATA = [
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "OnePage_one_page.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "OnePage_one_page.json"),
        name="OnePage",
        category="page",
        parser_lookup=parser_lookup,
        indexer=index_pbs_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "ThreePages_three_pages.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "ThreePages_three_pages.json"),
        name="ThreePages",
        category="page",
        parser_lookup=parser_lookup,
        indexer=index_pbs_strings,
    ),
]
PAGE_FAIL_TEST_DATA = [
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "ThreePages_three_pages.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "ThreePages_three_pages.json"),
        name="ThreePages",
        category="page",
        parser_lookup=parser_lookup,
        indexer=index_strings,
    ),
]


@pytest.mark.parametrize("test_data", PAGE_TEST_DATA)
def test_parser(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category
    json_path = output_path / f"{test_data.expected_data.file}"
    debug_path = output_path / f"{test_data.expected_data.file}_debug.txt"
    hashed_file = hashed_file_from_resource(test_data.input_data)
    with resources.as_file(test_data.input_data.file_resource()) as file_in:
        result = parse_file_to_json(
            file_in=file_in,
            indexer=test_data.indexer,
            parser_lookup=test_data.parser_lookup,
            file_out=json_path,
            debug_out=debug_path,
            source=hashed_file,
        )
    if not SERIALIZE_ONLY:
        with resources.as_file(
            test_data.expected_data.file_resource()
        ) as expected_file:
            expected = serialize.load_from_json(file_in=expected_file)
        assert result == expected
        # assert False


@pytest.mark.parametrize("test_data", PAGE_FAIL_TEST_DATA)
def test_parser_fail(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category / "fail"
    json_path = output_path / f"{test_data.expected_data.file}"
    debug_path = output_path / f"{test_data.expected_data.file}_debug.txt"
    with resources.as_file(test_data.input_data.file_resource()) as file_in:
        with pytest.raises(ParseException):
            result = parse_file_to_json(
                file_in=file_in,
                indexer=test_data.indexer,
                parser_lookup=test_data.parser_lookup,
                file_out=json_path,
                debug_out=debug_path,
            )
