from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.models.raw_2022_10 import lines


test_data = [
    lines.BaseEquipment(
        source=lines.SourceText(1, "BOS 737"),
        base="BOS",
        satelite_base="",
        equipment="737",
    ),
    lines.BaseEquipment(
        source=lines.SourceText(2, "LAX SAN 737"),
        base="LAX",
        satelite_base="SAN",
        equipment="737",
    ),
]


def test_base_equipment():
    ctx = ParseContextTest("None")
    expected_state = "base_equipment"
    parser = line_parser.BaseEquipment()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        assert data == ctx.parsed_data
