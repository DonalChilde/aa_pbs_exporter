from pathlib import Path

from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.parsing.indexed_string import IndexedString

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


def test_transportation_additional(test_app_data_dir: Path):
    run_line_test(
        name="test_transportation_additional",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="transportation_additional",
        parser=line_parser.TransportationAdditional(),
    )
