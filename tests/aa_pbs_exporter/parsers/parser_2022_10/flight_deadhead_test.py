from pathlib import Path

from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    lines.Flight(
        source=IndexedString(
            1,
            "4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31",
        ),
        dutyperiod_idx="4",
        dep_arr_day="4/4",
        eq_code="64",
        flight_number="2578",
        deadhead="D",
        departure_station="MIA",
        departure_time="1949/1649",
        meal="",
        arrival_station="SAN",
        arrival_time="2220/2220",
        block="0.00",
        synth="5.31",
        ground="0.00",
        equipment_change="",
        calendar="",
    ),
    lines.Flight(
        source=IndexedString(
            1,
            "2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X",
        ),
        dutyperiod_idx="2",
        dep_arr_day="2/2",
        eq_code="45",
        flight_number="1614",
        deadhead="D",
        departure_station="MCI",
        departure_time="1607/1407",
        meal="",
        arrival_station="DFW",
        arrival_time="1800/1600",
        block="0.00",
        synth="1.53",
        ground="1.27",
        equipment_change="X",
        calendar="",
    ),
]


def test_flight_deadhead(test_app_data_dir: Path):
    run_line_test(
        name="test_flight_deadhead",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="flight",
        parser=line_parser.FlightDeadhead(),
    )
