from pathlib import Path

from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString

test_data = [
    raw.TripFooter(
        source=IndexedString(
            1,
            "TTL                                              7.50   0.00   7.50        10.20       −− −− −−",
        ),
        block="7.50",
        synth="0.00",
        total_pay="7.50",
        tafb="10.20",
        calendar="−− −− −−",
    ),
    raw.TripFooter(
        source=IndexedString(
            2,
            "TTL                                             17.18   0.00  17.18        60.04",
        ),
        block="17.18",
        synth="0.00",
        total_pay="17.18",
        tafb="60.04",
        calendar="",
    ),
]


def test_trip_footer(test_app_data_dir: Path):
    run_line_test(
        name="test_trip_footer",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="trip_footer",
        parser=line_parser.TripFooter(),
    )
