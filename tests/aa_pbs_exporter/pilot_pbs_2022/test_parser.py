import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Dict, Sequence

import pyparsing as pp
import pytest
from pfmsoft.text_chunk_parser.text_chunk_parser import Chunk, ChunkParser

from aa_pbs_exporter.pilot_pbs_2022 import parser as pbs_parser


# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
@dataclass
class ParseTest:
    chunk: Chunk
    expected_state: str
    data: Dict = field(default_factory=dict)


def _parse_test(parse_tests: Sequence[ParseTest], parser: ChunkParser):
    for test in parse_tests:
        new_state, data = parser().parse(test.chunk, None, None)
        print("Data:\n", data)
        assert new_state == test.expected_state
        assert data == test.data


def test_footer(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               PHL 787  INTL                             PAGE  1990",
            ),
            expected_state="footer",
            data={
                "issued": date(2022, 4, 1),
                "effective": date(2022, 5, 1),
                "base": "PHL",
                "equipment": "787",
                "division": "INTL",
                "internal_page": "1990",
            },
        )
    ]
    _parse_test(tests, pbs_parser.FooterLine)


def test_first_header(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/",
            ),
            expected_state="first_header",
            data={},
        ),
    ]
    _parse_test(tests, pbs_parser.FirstHeaderLine)


def test_second_header(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01",
            ),
            expected_state="second_header",
            data={
                "calendar_from": {"day": 2, "month": 5},
                "calendar_to": {"day": 1, "month": 6},
            },
        ),
    ]
    _parse_test(tests, pbs_parser.SecondHeaderLine)


def test_dash_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
            ),
            expected_state="dash_line",
            data={},
        ),
    ]
    _parse_test(tests, pbs_parser.DashLine)


def test_base_eq_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(chunk_id="1", text="PHL 787"),
            expected_state="base_eq",
            data={"base": "PHL", "equipment": "787"},
        )
    ]
    _parse_test(tests, pbs_parser.BaseEqLine)


def test_sequence_header_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "SEQ 1313   28 OPS   POSN CA FO                GREEK OPERATION                          MO TU WE TH FR SA SU ",
            ),
            expected_state="sequence_header",
            data={
                "international_operation": "GREEK",
                "ops": 28,
                "positions": ["CA", "FO"],
                "sequence_number": "1313",
            },
        ),
    ]
    _parse_test(tests, pbs_parser.SequenceHeaderLine)


def test_report_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "                RPT 0800/0800                                                          −− −− −− −− −−  7 −−",
            ),
            expected_state="report",
            data={
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", 7, "−−"],
                "report_home": time(8, 0),
                "report_local": time(8, 0),
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                "                RPT 1545/1545                                                          −− −− −− −− −− −− −−",
            ),
            expected_state="report",
            data={
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
                "report_home": time(15, 45),
                "report_local": time(15, 45),
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                "                RPT 0652/0652",
            ),
            expected_state="report",
            data={
                "calendar_entries": [],
                "report_home": time(6, 52),
                "report_local": time(6, 52),
            },
        ),
    ]
    _parse_test(tests, pbs_parser.ReportLine)


def test_flight_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "2  2/2 26 2112  DFW 0600/0700  B LAX 0725/1025   3.25          2.35X",
            ),
            expected_state="flight",
            data={
                "duty_period": 2,
                "day_of_sequence": {"d": 2, "a": 2},
                "equipment_code": "26",
                "flight_number": "2112",
                "departure_city": "DFW",
                "departure_local": time(6, 0),
                "departure_home": time(7, 0),
                "crew_meal": "B",
                "arrival_city": "LAX",
                "arrival_local": time(7, 25),
                "arrival_home": time(10, 25),
                "block": timedelta(seconds=12300),
                "ground": timedelta(seconds=9300),
                "equipment_change": "X",
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                "1  1/1 64  508  MBJ 1306/1406    DFW 1700/1800   3.54                                  −− −− −− −− −− −− −−",
            ),
            expected_state="flight",
            data={
                "duty_period": 1,
                "day_of_sequence": {"d": 1, "a": 1},
                "equipment_code": "64",
                "flight_number": "508",
                "departure_city": "MBJ",
                "departure_local": time(13, 6),
                "departure_home": time(14, 6),
                "crew_meal": None,
                "arrival_city": "DFW",
                "arrival_local": time(17, 0),
                "arrival_home": time(18, 0),
                "block": timedelta(seconds=14040),
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
        ),
    ]
    _parse_test(tests, pbs_parser.FlightLine)


def test_release_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "                                 RLS 0054/0054   6.05   0.00   6.05  10.18        9.48 −− −− −−",
            ),
            expected_state="release",
            data={
                "release_local": time(0, 54),
                "release_home": time(0, 54),
                "block": timedelta(seconds=21900),
                "synth": timedelta(0),
                "total_pay": timedelta(seconds=21900),
                "duty": timedelta(seconds=37080),
                "flight_duty": timedelta(seconds=35280),
                "calendar_entries": ["−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                "                                 RLS 2203/2203   3.00   0.49   3.49   7.38        7.08",
            ),
            expected_state="release",
            data={
                "release_local": time(22, 3),
                "release_home": time(22, 3),
                "block": timedelta(seconds=10800),
                "synth": timedelta(seconds=2940),
                "total_pay": timedelta(seconds=13740),
                "duty": timedelta(seconds=27480),
                "flight_duty": timedelta(seconds=25680),
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                "                                 RLS 0825/0325   7.15   0.00   7.15   8.45        8.15 16 −− 18 −− −− −− −−",
            ),
            expected_state="release",
            data={
                "release_local": time(8, 25),
                "release_home": time(3, 25),
                "block": timedelta(seconds=26100),
                "synth": timedelta(0),
                "total_pay": timedelta(seconds=26100),
                "duty": timedelta(seconds=31500),
                "flight_duty": timedelta(seconds=29700),
                "calendar_entries": [16, "−−", 18, "−−", "−−", "−−", "−−"],
            },
        ),
    ]
    _parse_test(tests, pbs_parser.ReleaseLine)


def test_hotel_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "                LHR HI HIGH STREET                          442073684023   23.50       −− −− 25 −− −− −− −−",
            ),
            expected_state="hotel",
            data={
                "layover_city": "LHR",
                "hotel": "HI HIGH STREET",
                "hotel_phone": ["442073684023"],
                "rest": timedelta(seconds=85800),
                "calendar_entries": ["−−", "−−", 25, "−−", "−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                "                ATH HOTEL INFO IN CCI/CREW PORTAL                          25.10       −− −− −− −− −− −− −−",
            ),
            expected_state="hotel",
            data={
                "layover_city": "ATH",
                "hotel": "HOTEL INFO IN CCI/CREW PORTAL",
                "hotel_phone": [],
                "rest": timedelta(days=1, seconds=4200),
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                "                BDL SHERATON SPRINGFIELD MONARCH PLACE HOTE 14137811010    21.02",
            ),
            expected_state="hotel",
            data={
                "layover_city": "BDL",
                "hotel": "SHERATON SPRINGFIELD MONARCH PLACE HOTE",
                "hotel_phone": ["14137811010"],
                "rest": timedelta(seconds=75720),
                "calendar_entries": [],
            },
        ),
    ]
    _parse_test(tests, pbs_parser.HotelLine)


def test_additional_hotel_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "4",
                "               +LAS THE WESTIN LAS VEGAS HOTEL              17028365900",
            ),
            expected_state="additional_hotel",
            data={
                "layover_city": "LAS",
                "hotel": "THE WESTIN LAS VEGAS HOTEL",
                "hotel_phone": "17028365900",
                "calendar_entries": [],
            },
        ),
    ]
    _parse_test(tests, pbs_parser.AdditionalHotelLine)


def test_transportation_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "                    COMET CAR HIRE (CCH) LTD                442088979984               −− −− −−",
            ),
            expected_state="transportation",
            data={
                "transportation": "COMET CAR HIRE (CCH) LTD",
                "transportation_phone": ["442088979984"],
                "calendar_entries": ["−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                "                    TRANS INFO IN CCI/CREW PORTAL                                      −− −−  1",
            ),
            expected_state="transportation",
            data={
                "transportation": "TRANS INFO IN CCI/CREW PORTAL",
                "transportation_phone": [],
                "calendar_entries": ["−−", "−−", 1],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                "                    SHUTTLE",
            ),
            expected_state="transportation",
            data={
                "transportation": "SHUTTLE",
                "transportation_phone": [],
                "calendar_entries": [],
            },
        ),
    ]
    _parse_test(tests, pbs_parser.TransportationLine)


def test_total_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                "TTL                                             15.47   0.37  16.24        57.26",
            ),
            expected_state="total",
            data={
                "block": timedelta(seconds=56820),
                "synth": timedelta(seconds=2220),
                "total_pay": timedelta(seconds=59040),
                "tafb": timedelta(days=2, seconds=33960),
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                "TTL                                              4.58   0.17   5.15         7.18       −− −− −−",
            ),
            expected_state="total",
            data={
                "block": timedelta(seconds=17880),
                "synth": timedelta(seconds=1020),
                "total_pay": timedelta(seconds=18900),
                "tafb": timedelta(seconds=26280),
                "calendar_entries": ["−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                "TTL                                              4.54   0.21   5.15         7.16       30 −−  1",
            ),
            expected_state="total",
            data={
                "block": timedelta(seconds=17640),
                "synth": timedelta(seconds=1260),
                "total_pay": timedelta(seconds=18900),
                "tafb": timedelta(seconds=26160),
                "calendar_entries": [30, "−−", 1],
            },
        ),
    ]
    _parse_test(tests, pbs_parser.TotalLine)
