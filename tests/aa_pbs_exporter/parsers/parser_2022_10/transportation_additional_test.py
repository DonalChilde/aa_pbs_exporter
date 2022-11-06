from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.indexed_string import IndexedString

test_data = [
    lines.TransportationAdditional(
        source=IndexedString(
            1,
            "                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
        ),
        name="SKY TRANSPORTATION SERVICE, LLC",
        phone="8566169633",
        calendar="",
    ),
    lines.TransportationAdditional(
        source=IndexedString(
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
    parser = line_parser.TransportationAdditional()
    for data in test_data:
        state = parser.parse(data.source, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
