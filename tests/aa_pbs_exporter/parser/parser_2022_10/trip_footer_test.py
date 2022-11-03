from tests.aa_pbs_exporter.parser.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import raw_lines as raw
from aa_pbs_exporter.parser import parser_2022_10 as parsers

test_data = [
    raw.TripFooter(
        source=raw.SourceText(
            1,
            "TTL                                              7.50   0.00   7.50        10.20       −− −− −−",
        ),
        block="7.50",
        synth="0.00",
        total_pay="7.50",
        tafb="10.20",
        calendar="−− −− −−",
    ),
    raw.TripFooter(
        source=raw.SourceText(
            2,
            "TTL                                             17.18   0.00  17.18        60.04",
        ),
        block="17.18",
        synth="0.00",
        total_pay="17.18",
        tafb="60.04",
        calendar="",
    ),
]


def test_trip_footer():
    ctx = ParseContextTest("None")
    expected_state = "trip_footer"
    parser = parsers.TripFooter()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
