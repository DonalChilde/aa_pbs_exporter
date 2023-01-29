from pathlib import Path

from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString

test_data = [
    raw.TransportationAdditional(
        source=raw.IndexedString(
            idx=1,
            txt="                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
        ),
        name="SKY TRANSPORTATION SERVICE, LLC",
        phone="8566169633",
        calendar="",
    ),
    raw.TransportationAdditional(
        source=raw.IndexedString(
            idx=2,
            txt="                    DESERT COACH                            6022866161",
        ),
        name="DESERT COACH",
        phone="6022866161",
        calendar="",
    ),
]


def test_transportation_additional(test_app_data_dir: Path):
    run_line_test(
        name="test_transportation_additional",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="transportation_additional",
        parser=line_parser.TransportationAdditional(),
    )
