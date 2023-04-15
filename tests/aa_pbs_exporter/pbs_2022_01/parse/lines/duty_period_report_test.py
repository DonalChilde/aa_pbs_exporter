from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parsers as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import DutyPeriodReport, IndexedString
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="duty_period_report_1",
        txt="""                RPT 1237/1237                                                           2 −− −− −− −− −− −−""",
        description="Duty period report with a calendar.",
    ),
]
result_data = {
    "duty_period_report_1": ParseResult(
        current_state="dutyperiod_report",
        parsed_data=DutyPeriodReport(
            source=IndexedString(
                idx=1,
                txt="                RPT 1237/1237                                                           2 −− −− −− −− −− −−",
            ),
            report="1237/1237",
            calendar="2 −− −− −− −− −− −−",
        ),
    )
}


PARSER = line_parser.DutyPeriodReport()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "duty_period_report"
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
