from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser

test_data = [
    lines.Hotel(
        source=lines.SourceText(
            1,
            "                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
        ),
        layover_city="MIA",
        name="SONESTA MIAMI AIRPORT",
        phone="13054469000",
        rest="11.27",
        calendar="−− −− −− −− −− −− −−",
    ),
    lines.Hotel(
        source=lines.SourceText(
            2,
            "                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
        ),
        layover_city="LHR",
        name="PARK PLAZA WESTMINSTER BRIDGE LONDON",
        phone="443334006112",
        rest="24.00",
        calendar="−− −− −− −− −− −− −−",
    ),
]


def test_hotel():
    ctx = ParseContextTest("None")
    expected_state = "hotel"
    parser = line_parser.Hotel()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
