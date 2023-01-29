from pathlib import Path

from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString

test_data = [
    raw.HotelAdditional(
        source=raw.IndexedString(
            idx=1,
            txt="               +PHL MARRIOTT OLD CITY                       12152386000",
        ),
        layover_city="PHL",
        name="MARRIOTT OLD CITY",
        phone="12152386000",
        calendar="",
    ),
    raw.HotelAdditional(
        source=raw.IndexedString(
            idx=2,
            txt="               +PHL CAMBRIA HOTEL AND SUITES                12157325500",
        ),
        layover_city="PHL",
        name="CAMBRIA HOTEL AND SUITES",
        phone="12157325500",
        calendar="",
    ),
]


def test_hotel_additional(test_app_data_dir: Path):
    run_line_test(
        name="test_hotel_additional",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="hotel_additional",
        parser=line_parser.HotelAdditional(),
    )
