from pathlib import Path

from devtools import debug
from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    raw.TripHeader(
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
    raw.TripHeader(
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
    raw.TripHeader(
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
