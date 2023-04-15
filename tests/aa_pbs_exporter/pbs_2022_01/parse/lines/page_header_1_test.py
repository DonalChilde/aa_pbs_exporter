from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parsers as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import IndexedString, PageHeader1
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="page_header1_1",
        txt="""   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/""",
        description="This is a description of the particular type of line",
    )
]


result_data = {
    "page_header1_1": ParseResult(
        current_state="page_header_1",
        parsed_data=PageHeader1(
            source=IndexedString(
                idx=1,
                txt="\x0c   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/",
            )
        ),
    )
}

PARSER = line_parser.PageHeader1()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "page_header1"
    parse_lines(
        test_data=test_data,
        result_data=result_data,
        parser=PARSER,
        output_path=outpath,
        skip_test=False,
    )


def test_parse_fail():
    with pytest.raises(ParseException):
        PARSER.parse(IndexedString(idx=1, txt="foo"), ctx={})
