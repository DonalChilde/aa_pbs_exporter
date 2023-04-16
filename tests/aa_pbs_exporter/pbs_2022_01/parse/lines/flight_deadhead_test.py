from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parsers as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import Flight, IndexedString
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_exception import (
    ParseException,
)

test_data = [
    ParseTestData(
        name="flight_deadhead_1",
        txt="4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="flight_deadhead_2",
        txt="2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "flight_deadhead_1": ParseResult(
        current_state="flight",
        parsed_data=Flight(
            source=IndexedString(
                idx=1,
                txt="4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31",
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
    ),
    "flight_deadhead_2": ParseResult(
        current_state="flight",
        parsed_data=Flight(
            source=IndexedString(
                idx=2,
                txt="2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X",
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
    ),
}

PARSER = line_parser.FlightDeadhead()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "flight_deadhead"
    parse_lines(
        test_data=test_data,
        result_data=result_data,
        parser=PARSER,
        output_path=outpath,
        skip_test=False,
    )


def test_parse_fail():
    with pytest.raises(ParseException):
        PARSER.parse(IndexedString(idx=1, txt="foo"), ctx={})


# test_data = [
#     raw.Flight(
#         source=raw.IndexedString(
#             idx=1,
#             txt="4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31",
#         ),
#         dutyperiod_idx="4",
#         dep_arr_day="4/4",
#         eq_code="64",
#         flight_number="2578",
#         deadhead="D",
#         departure_station="MIA",
#         departure_time="1949/1649",
#         meal="",
#         arrival_station="SAN",
#         arrival_time="2220/2220",
#         block="0.00",
#         synth="5.31",
#         ground="0.00",
#         equipment_change="",
#         calendar="",
#     ),
#     raw.Flight(
#         source=raw.IndexedString(
#             idx=1,
#             txt="2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X",
#         ),
#         dutyperiod_idx="2",
#         dep_arr_day="2/2",
#         eq_code="45",
#         flight_number="1614",
#         deadhead="D",
#         departure_station="MCI",
#         departure_time="1607/1407",
#         meal="",
#         arrival_station="DFW",
#         arrival_time="1800/1600",
#         block="0.00",
#         synth="1.53",
#         ground="1.27",
#         equipment_change="X",
#         calendar="",
#     ),
# ]


# def test_flight_deadhead(test_app_data_dir: Path):
#     run_line_test(
#         name="test_flight_deadhead",
#         output_dir=test_app_data_dir,
#         test_data=test_data,
#         expected_state="flight",
#         parser=line_parser.FlightDeadhead(),
#     )
