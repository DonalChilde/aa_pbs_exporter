from tests.aa_pbs_exporter.parser.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.parser import parser_2022_10 as parsers

test_data = [
    raw.PageFooter(
        source=raw.SourceText(
            1,
            "                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
        ),
        issued="MIA",
        effective="SONESTA MIAMI AIRPORT",
        base="13054469000",
        satelite_base="11.27",
        equipment="",
        division="",
        page="−− −− −− −− −− −− −−",
    ),
    raw.PageFooter(
        source=raw.SourceText(
            2,
            "                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
        ),
        issued="MIA",
        effective="SONESTA MIAMI AIRPORT",
        base="13054469000",
        satelite_base="11.27",
        equipment="",
        division="",
        page="−− −− −− −− −− −− −−",
    ),
]


def test_page_footer():
    ctx = ParseContextTest("None")
    expected_state = "page_footer"
    parser = parsers.PageFooter()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
