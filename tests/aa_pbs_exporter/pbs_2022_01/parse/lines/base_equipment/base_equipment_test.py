import json
from importlib import resources
from logging import Logger
from pathlib import Path

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import parsers_td
from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme_td import ParserLookupSingle
from aa_pbs_exporter.snippets.indexed_string.typedict.index_strings import index_strings
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseException,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_file_to_json import (
    parse_file_to_json,
)
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData

PARSER = parsers_td.BaseEquipment()
SERIALIZE_ONLY = False
TEST_DATA = [
    ResourceTestData("satellite_base.txt", "satellite_base.json"),
    ResourceTestData("no_satellite_base.txt", "no_satellite_base.json"),
]


TEST_FAIL = [ResourceTestData("fail.txt", "fail.json")]


def test_parser(test_app_data_dir: Path, logger: Logger):
    output_path = test_app_data_dir / "lines" / PARSER.__class__.__qualname__
    res_dir = resources.files(__package__)
    parser_lookup = ParserLookupSingle(PARSER)
    for item in TEST_DATA:
        res_file = res_dir.joinpath(item.input_data)
        json_path = output_path / f"{item.result_data}"
        debug_path = output_path / f"{item.input_data}_debug.txt"
        with resources.as_file(res_file) as file_in:
            result = parse_file_to_json(
                file_in=file_in,
                indexer=index_strings,
                parser_lookup=parser_lookup,
                file_out=json_path,
                debug_out=debug_path,
            )
        if not SERIALIZE_ONLY:
            expected_file = res_dir.joinpath(item.result_data)
            expected = json.loads(expected_file.read_text())
            assert result == expected


def test_parser_fail(test_app_data_dir: Path, logger: Logger):
    output_path = test_app_data_dir / "lines" / PARSER.__class__.__qualname__
    res_dir = resources.files(__package__)
    parser_lookup = ParserLookupSingle(PARSER)
    for item in TEST_FAIL:
        res_file = res_dir.joinpath(item.input_data)
        json_path = output_path / f"{item.result_data}"
        debug_path = output_path / f"{item.input_data}_debug.txt"
        with resources.as_file(res_file) as file_in:
            with pytest.raises(ParseException):
                result = parse_file_to_json(
                    file_in=file_in,
                    indexer=index_strings,
                    parser_lookup=parser_lookup,
                    file_out=json_path,
                    debug_out=debug_path,
                )


# def test_parse_fail(test_app_data_dir: Path, logger: Logger):
#     output_path = test_app_data_dir / "lines" / PARSER.__class__.__qualname__
#     for fail_data in TEST_FAIL:
#         with pytest.raises(ParseException):
#             process_lines(
#                 package=__package__,
#                 data=fail_data,
#                 path_out=output_path,
#                 parser=PARSER,
#                 model=MODEL,
#                 serialize_only=True,
#             )


# def test_lines(test_app_data_dir: Path, logger: Logger):
#     output_path = test_app_data_dir / "lines" / PARSER.__class__.__qualname__
#     for data in TEST_DATA:
#         process_lines(
#             package=__package__,
#             data=data,
#             path_out=output_path,
#             parser=PARSER,
#             model=MODEL,
#             serialize_only=SERIALIZE_ONLY,
#         )
#     assert not SERIALIZE_ONLY
