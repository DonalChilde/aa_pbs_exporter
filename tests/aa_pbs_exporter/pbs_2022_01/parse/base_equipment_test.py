from pathlib import Path

from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    raw.BaseEquipment(
        source=IndexedString(1, "BOS 737"),
        base="BOS",
        satelite_base="",
        equipment="737",
    ),
    raw.BaseEquipment(
        source=IndexedString(2, "LAX SAN 737"),
        base="LAX",
        satelite_base="SAN",
        equipment="737",
    ),
]


def test_base_equipment(test_app_data_dir: Path):
    run_line_test(
        name="test_base_equipment",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="base_equipment",
        parser=line_parser.BaseEquipment(),
    )
