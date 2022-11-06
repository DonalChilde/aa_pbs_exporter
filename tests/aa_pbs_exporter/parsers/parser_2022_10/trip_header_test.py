from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.indexed_string import IndexedString

test_data = [
    lines.TripHeader(
        source=IndexedString(
            1,
            "SEQ 25064   1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU",
        ),
        number="25064",
        ops_count="1",
        positions="CA FO",
        operations="",
        special_qualification="",
        calendar="",
    ),
    lines.TripHeader(
        source=IndexedString(
            1,
            "SEQ 6292    1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU",
        ),
        number="6292",
        ops_count="1",
        positions="CA FO",
        operations="SPANISH",
        special_qualification="",
        calendar="",
    ),
    lines.TripHeader(
        source=IndexedString(
            1,
            "SEQ 16945   1 OPS   POSN CA FO                SPECIAL QUALIFICATION                    MO TU WE TH FR SA SU",
        ),
        number="16945",
        ops_count="1",
        positions="CA FO",
        operations="",
        special_qualification="SPECIAL QUALIFICATION",
        calendar="",
    ),
]


def test_trip_header():
    ctx = ParseContextTest("None")
    expected_state = "trip_header"
    parser = line_parser.TripHeader()
    for data in test_data:
        state = parser.parse(data.source, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
