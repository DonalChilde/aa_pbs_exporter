from pathlib import Path
from aa_pbs_exporter.util.parsing.parse_context import DevParseContext
from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.parsing.indexed_string import IndexedString
from tests.aa_pbs_exporter.resources.helpers import run_line_test

test_data = [
    lines.Flight(
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
