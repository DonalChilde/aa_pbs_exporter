from pathlib import Path

from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    raw.Flight(
        source=IndexedString(
            1,
            "1  1/1 65 2131  SAN 1337/1337    ORD 1935/1735   3.58          1.10X                   −− −− −− −− −− −− −−",
        ),
        dutyperiod_idx="1",
        dep_arr_day="1/1",
        eq_code="65",
        flight_number="2131",
        deadhead="",
        departure_station="SAN",
        departure_time="1337/1337",
        meal="",
        arrival_station="ORD",
        arrival_time="1935/1735",
        block="3.58",
        synth="0.00",
        ground="1.10",
        equipment_change="X",
        calendar="−− −− −− −− −− −− −−",
    ),
]


def test_flight(test_app_data_dir: Path):
    run_line_test(
        name="test_flight",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="flight",
        parser=line_parser.Flight(),
    )
