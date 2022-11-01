from tests.aa_pbs_exporter.parser.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.parser import parser_2022_10 as parsers

test_data = [
    raw.TransportationAdditional(
        source=raw.SourceText(
            1,
            "                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
        ),
        name="SKY TRANSPORTATION SERVICE, LLC",
        phone="8566169633",
        calendar="",
    ),
    raw.TransportationAdditional(
        source=raw.SourceText(
            2,
            "                    DESERT COACH                            6022866161",
        ),
        name="DESERT COACH",
        phone="6022866161",
        calendar="",
    ),
]


def test_transportation_additional():
    ctx = ParseContextTest("None")
    expected_state = "transportation_additional"
    parser = parsers.TransportationAdditional()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
