from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parsers as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import DutyPeriodRelease, IndexedString
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_exception import (
    ParseException,
)

test_data = [
    ParseTestData(
        name="duty_period_release_1",
        txt="""                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−""",
        description="duty period release with calendar",
    ),
    ParseTestData(
        name="duty_period_release_2",
        txt="""                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00""",
        description="duty period release without calendar",
    ),
]

result_data = {
    "duty_period_release_1": ParseResult(
        current_state="dutyperiod_release",
        parsed_data=DutyPeriodRelease(
            source=IndexedString(
                idx=1,
                txt="                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−",
            ),
            release="0739/0439",
            block="4.49",
            synth="0.00",
            total_pay="4.49",
            duty="6.19",
            flight_duty="5.49",
            calendar="−− −− −− −− −− −− −−",
        ),
    ),
    "duty_period_release_2": ParseResult(
        current_state="dutyperiod_release",
        parsed_data=DutyPeriodRelease(
            source=IndexedString(
                idx=2,
                txt="                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00",
            ),
            release="2252/2252",
            block="0.00",
            synth="5.46",
            total_pay="5.46",
            duty="6.46",
            flight_duty="0.00",
            calendar="",
        ),
    ),
}


PARSER = line_parser.DutyPeriodRelease()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "duty_period_release"
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


# test_data = [
#     raw.DutyPeriodRelease(
#         source=raw.IndexedString(
#             idx=1,
#             txt="                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−",
#         ),
#         release="0739/0439",
#         block="4.49",
#         synth="0.00",
#         total_pay="4.49",
#         duty="6.19",
#         flight_duty="5.49",
#         calendar="−− −− −− −− −− −− −−",
#     ),
#     raw.DutyPeriodRelease(
#         source=raw.IndexedString(
#             idx=1,
#             txt="                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00",
#         ),
#         release="2252/2252",
#         block="0.00",
#         synth="5.46",
#         total_pay="5.46",
#         duty="6.46",
#         flight_duty="0.00",
#         calendar="",
#     ),
# ]


# def test_dutyperiod_release(test_app_data_dir: Path):
#     run_line_test(
#         name="test_dutyperiod_release",
#         output_dir=test_app_data_dir,
#         test_data=test_data,
#         expected_state="dutyperiod_release",
#         parser=line_parser.DutyPeriodRelease(),
#     )
