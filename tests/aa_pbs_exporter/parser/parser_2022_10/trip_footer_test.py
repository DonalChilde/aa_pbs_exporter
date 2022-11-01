from tests.aa_pbs_exporter.parser.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.parser import parser_2022_10 as parsers

test_data = [
    raw.TripFooter(
        source=raw.SourceText(
            1,
            "                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
        ),
        block="MIA",
        synth="SONESTA MIAMI AIRPORT",
        total_pay="13054469000",
        tafb="11.27",
        calendar="−− −− −− −− −− −− −−",
    ),
    raw.TripFooter(
        source=raw.SourceText(
            2,
            "                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
        ),
        block="MIA",
        synth="SONESTA MIAMI AIRPORT",
        total_pay="13054469000",
        tafb="11.27",
        calendar="−− −− −− −− −− −− −−",
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
