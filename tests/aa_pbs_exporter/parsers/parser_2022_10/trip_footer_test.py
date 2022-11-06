from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.indexed_string import IndexedString

test_data = [
    lines.TripFooter(
        source=IndexedString(
            1,
            "TTL                                              7.50   0.00   7.50        10.20       −− −− −−",
        ),
        block="7.50",
        synth="0.00",
        total_pay="7.50",
        tafb="10.20",
        calendar="−− −− −−",
    ),
    lines.TripFooter(
        source=IndexedString(
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
    parser = line_parser.TripFooter()
    for data in test_data:
        state = parser.parse(data.source, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
