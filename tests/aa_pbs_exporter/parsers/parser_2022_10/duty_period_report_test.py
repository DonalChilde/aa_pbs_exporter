from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser

test_data = [
    lines.DutyPeriodReport(
        source=lines.SourceText(
            1,
            "                RPT 1237/1237                                                           2 −− −− −− −− −− −−",
        ),
        report="1237/1237",
        calendar="2 −− −− −− −− −− −−",
    ),
]


def test_dutyperiod_report():
    ctx = ParseContextTest("None")
    expected_state = "dutyperiod_report"
    parser = line_parser.DutyPeriodReport()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
