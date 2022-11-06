from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.indexed_string import IndexedString

test_data = [
    lines.HotelAdditional(
        source=IndexedString(
            1,
            "               +PHL MARRIOTT OLD CITY                       12152386000",
        ),
        layover_city="PHL",
        name="MARRIOTT OLD CITY",
        phone="12152386000",
        calendar="",
    ),
    lines.HotelAdditional(
        source=IndexedString(
            2,
            "               +PHL CAMBRIA HOTEL AND SUITES                12157325500",
        ),
        layover_city="PHL",
        name="CAMBRIA HOTEL AND SUITES",
        phone="12157325500",
        calendar="",
    ),
]


def test_hotel_additional():
    ctx = ParseContextTest("None")
    expected_state = "hotel_additional"
    parser = line_parser.HotelAdditional()
    for data in test_data:
        state = parser.parse(data.source, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
