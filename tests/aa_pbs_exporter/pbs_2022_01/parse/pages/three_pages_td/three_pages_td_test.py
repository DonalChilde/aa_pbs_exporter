from importlib import resources
import json
import logging
from pathlib import Path

from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData
from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme_td import parser_lookup

from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_file_to_json import (
    parse_file_to_json,
)
from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_strings_td import index_pbs_strings

TEST_DATA = ResourceTestData("three_pages.txt", "three_pages.json")


def test_parse(
    test_app_data_dir: Path,
    logger: logging.Logger,
):
    output_path = test_app_data_dir / "pages" / __name__.rsplit(".", maxsplit=1)[-1]
    res_dir = resources.files(__package__)
    res_file = res_dir.joinpath(TEST_DATA.input_data)
    json_path = output_path / f"{TEST_DATA.result_data}"
    debug_path = output_path / f"{TEST_DATA.input_data}_debug.txt"
    with resources.as_file(res_file) as file_in:
        result = parse_file_to_json(
            file_in=file_in,
            indexer=index_pbs_strings,
            parser_lookup=parser_lookup,
            file_out=json_path,
            debug_out=debug_path,
        )
    expected_file = res_dir.joinpath(TEST_DATA.result_data)
    expected = json.loads(expected_file.read_text())
    assert result == expected


# def parse_file(
#     file_in: Path,
#     parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]],
#     file_out: Path | None = None,
#     debug_out: Path | None = None,
# ):
#     time_logger = timers.TimeLogger(logger=logger, level=logging.INFO)
#     with timers.ContextTimer(time_logger, ident=__name__):
#         with open(file_in, encoding="utf-8") as txt_file:
#             indexed_strings = index_pbs_strings(txt_file)
#             # result_handler = DebugParse(debug_path, foo="foo test")
#             result_handler = SaveAsJson(
#                 file_out=file_out, debug_out=debug_out, foo="foo test"
#             )
#             result = parse_job(
#                 indexed_strings=indexed_strings,
#                 parser_lookup=parser_lookup,
#                 result_handler=result_handler,
#                 ctx={},
#             )
