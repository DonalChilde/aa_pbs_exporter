from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import IndexedString, PageHeader2
from aa_pbs_exporter.pbs_2022_01.parse import ParseResultProtocol
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="page_header2_1",
        txt="DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01",
        description="A base equipment with no satellite base",
    ),
]


result_data = {
    "page_header2_1": ParseResultProtocol(
        current_state="page_header_2",
        parsed_data=PageHeader2(
            source=IndexedString(
                idx=1,
                txt="DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01",
            ),
            from_date="05/02",
            to_date="06/01",
        ),
    )
}


PARSER = line_parser.PageHeader2()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "page_header2"
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
