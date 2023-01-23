from pathlib import Path

from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    lines.BaseEquipment(
        source=IndexedString(1, "BOS 737"),
        base="BOS",
        satelite_base="",
        equipment="737",
    ),
    lines.BaseEquipment(
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
