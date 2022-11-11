from pathlib import Path

from devtools import debug
from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.parsing.indexed_string import IndexedString
from aa_pbs_exporter.util.parsing.parse_context import DevParseContext
from tests.aa_pbs_exporter.resources.helpers import run_line_test

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


def test_trip_header(test_app_data_dir: Path):
    run_line_test(
        name="test_trip_header",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="trip_header",
        parser=line_parser.TripHeader(),
    )
