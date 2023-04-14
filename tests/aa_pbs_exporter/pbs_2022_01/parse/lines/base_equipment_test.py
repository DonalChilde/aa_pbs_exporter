from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import BaseEquipment, IndexedString
from aa_pbs_exporter.pbs_2022_01.parse import ParseResultProtocol
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="base_equipment_1",
        txt="""BOS 737""",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="base_equipment_2",
        txt="""LAX SAN 737""",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "base_equipment_1": ParseResultProtocol(
        current_state="base_equipment",
        parsed_data=BaseEquipment(
            source=IndexedString(idx=1, txt="BOS 737"),
            base="BOS",
            satellite_base="",
            equipment="737",
        ),
    ),
    "base_equipment_2": ParseResultProtocol(
        current_state="base_equipment",
        parsed_data=BaseEquipment(
            source=IndexedString(idx=2, txt="LAX SAN 737"),
            base="LAX",
            satellite_base="SAN",
            equipment="737",
        ),
    ),
}


PARSER = line_parser.BaseEquipment()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "base_equipment"
    parse_lines(
        test_data=test_data,
        result_data=result_data,
        parser=PARSER,
        output_path=outpath,
        # skip_test=True,
    )


def test_parse_fail():
    with pytest.raises(ParseException):
        PARSER.parse(IndexedString(idx=1, txt="foo"), ctx={})
