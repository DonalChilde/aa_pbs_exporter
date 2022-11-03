from tests.aa_pbs_exporter.parser.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import raw_lines as raw
from aa_pbs_exporter.parser import parser_2022_10 as parsers

test_data = [
    raw.TripHeader(
        source=raw.SourceText(
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
    raw.TripHeader(
        source=raw.SourceText(
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
    raw.TripHeader(
        source=raw.SourceText(
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
    parser = parsers.TripHeader()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
