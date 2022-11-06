from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.indexed_string import IndexedString

test_data = [
    lines.TripSeparator(
        source=IndexedString(
            1,
            "−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
        ),
    ),
]


def test_trip_separator():
    ctx = ParseContextTest("None")
    expected_state = "trip_separator"
    parser = line_parser.TripSeparator()
    for data in test_data:
        state = parser.parse(data.source, ctx)
        assert state == expected_state
        assert data == ctx.parsed_data
