from tests.aa_pbs_exporter.parser.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import raw_lines as raw
from aa_pbs_exporter.parser import parser_2022_10 as parsers

test_data = [
    raw.DutyPeriodRelease(
        source=raw.SourceText(
            1,
            "                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−",
        ),
        release="0739/0439",
        block="4.49",
        synth="0.00",
        total_pay="4.49",
        duty="6.19",
        flight_duty="5.49",
        calendar="−− −− −− −− −− −− −−",
    ),
    raw.DutyPeriodRelease(
        source=raw.SourceText(
            1,
            "                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00",
        ),
        release="2252/2252",
        block="0.00",
        synth="5.46",
        total_pay="5.46",
        duty="6.46",
        flight_duty="0.00",
        calendar="",
    ),
]


def test_dutyperiod_release():
    ctx = ParseContextTest("None")
    expected_state = "dutyperiod_release"
    parser = parsers.DutyPeriodRelease()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
