from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parse_v2 as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import HeaderSeparator, IndexedString
from aa_pbs_exporter.pbs_2022_01.parse_v2 import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="header_separator_1",
        txt="−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
        description="header separator",
    ),
]

result_data = {
    "header_separator_1": ParseResult(
        current_state="header_separator",
        parsed_data=HeaderSeparator(
            source=IndexedString(
                idx=1,
                txt="−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
            )
        ),
    )
}


PARSER = line_parser.HeaderSeparator()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "header_separator"
    parse_lines(
        test_data=test_data,
        result_data=result_data,
        parser=PARSER,
        output_path=outpath,
        # skip_test=True,
    )


def test_parse_fail():
    with pytest.raises(ParseException):
        PARSER.parse(IndexedString(idx=1, txt="foo"), ctx={})
