import logging
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import Dict, Sequence

from pfmsoft.text_chunk_parser.text_chunk_parser import (
    Chunk,
    ChunkParser,
    FailedParseException,
)

from aa_pbs_exporter.pilot_pbs_2022 import parser_2 as pbs_parser


# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
@dataclass
class ParseTest:
    chunk: Chunk
    expected_state: str
    data: Dict = field(default_factory=dict)


def _parse_test(parse_tests: Sequence[ParseTest], parser: ChunkParser):
    for test in parse_tests:
        try:
            new_state, data = parser().parse(test.chunk, None, None)
        except FailedParseException as exc:
            print(exc.__context__.explain())  # pylint: disable=no-member
            assert False
        print("Data:\n", data)
        assert new_state == test.expected_state
        assert data == test.data


def test_footer(caplog, logger: logging.Logger):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                __name__,
                "COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               PHL 787  INTL                             PAGE  1990",
            ),
            expected_state="footer",
            data={
                "issued": "08APR2022",
                "effective": "02MAY2022",
                "base": "PHL",
                "equipment": "787",
                "division": "INTL",
                "internal_page": "1990",
            },
        )
    ]
    logger.info(tests)
    _parse_test(tests, pbs_parser.FooterLine)


def test_first_header(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                __name__,
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
                __name__,
                "DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01",
            ),
            expected_state="second_header",
            data={
                "calendar_from": {"month": "05", "day": "02"},
                "calendar_to": {"month": "06", "day": "01"},
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
                __name__,
                "−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
            ),
            expected_state="dash_line",
            data={},
        ),
    ]
    _parse_test(tests, pbs_parser.DashLine)


def test_base_equipment_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(chunk_id="1", source=__name__, text="PHL 787"),
            expected_state="base_equipment",
            data={"base": "PHL", "equipment": "787"},
        )
    ]
    _parse_test(tests, pbs_parser.BaseEquipmentLine)


def test_sequence_header_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                __name__,
                "SEQ 1313   28 OPS   POSN CA FO                GREEK OPERATION                          MO TU WE TH FR SA SU ",
            ),
            expected_state="sequence_header",
            data={
                "sequence": "1313",
                "ops_count": "28",
                "positions": ["CA", "FO"],
                "operations": ["GREEK"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                __name__,
                "SEQ 30533   1 OPS   POSN CA FO                                                         Replaces prior month",
            ),
            expected_state="sequence_header",
            data={
                "sequence": "30533",
                "ops_count": "1",
                "positions": ["CA", "FO"],
                "operations": [],
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
                __name__,
                "                RPT 0800/0800                                                          −− −− −− −− −−  7 −−",
            ),
            expected_state="report",
            data={
                "report_local": "0800",
                "report_home": "0800",
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "7", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                __name__,
                "                RPT 1545/1545                                                          −− −− −− −− −− −− −−",
            ),
            expected_state="report",
            data={
                "report_local": "1545",
                "report_home": "1545",
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                __name__,
                "                RPT 0652/0652",
            ),
            expected_state="report",
            data={
                "report_local": "0652",
                "report_home": "0652",
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "4",
                __name__,
                "                RPT 0730/0730                                                          sequence 5144/30APR",
            ),
            expected_state="report",
            data={
                "report_local": "0730",
                "report_home": "0730",
                "calendar_entries": [],
                "sequence_number": "5144",
                "date": ["30", "APR"],
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
                __name__,
                "2  2/2 26 2112  DFW 0600/0700  B LAX 0725/1025   3.25          2.35X",
            ),
            expected_state="flight",
            data={
                "dutyperiod": "2",
                "day_of_sequence": "2/2",
                "equipment_code": "26",
                "flight_number": "2112",
                "departure_city": "DFW",
                "departure_local": "0600",
                "departure_home": "0700",
                "crew_meal": "B",
                "arrival_city": "LAX",
                "arrival_local": "0725",
                "arrival_home": "1025",
                "block": "3.25",
                "ground": "2.35",
                "equipment_change": "X",
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                __name__,
                "1  1/1 64  508  MBJ 1306/1406    DFW 1700/1800   3.54                                  −− −− −− −− −− −− −−",
            ),
            expected_state="flight",
            data={
                "dutyperiod": "1",
                "day_of_sequence": "1/1",
                "equipment_code": "64",
                "flight_number": "508",
                "departure_city": "MBJ",
                "departure_local": "1306",
                "departure_home": "1406",
                "arrival_city": "DFW",
                "arrival_local": "1700",
                "arrival_home": "1800",
                "block": "3.54",
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
        ),
    ]

    _parse_test(tests, pbs_parser.FlightLine)


def test_flight_deadhead_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                __name__,
                "1  1/1 45  435D MIA 1010/1010    CLT 1225/1225    AA    2.15                           −− −− −− −− −− −− −−\n",
            ),
            expected_state="flight_deadhead",
            data={
                "dutyperiod": "1",
                "day_of_sequence": "1/1",
                "equipment_code": "45",
                "flight_number": "435",
                "deadhead": "D",
                "departure_city": "MIA",
                "departure_local": "1010",
                "departure_home": "1010",
                "arrival_city": "CLT",
                "arrival_local": "1225",
                "arrival_home": "1225",
                "deadhead_block": "AA",
                "synth": "2.15",
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                __name__,
                "1  1/1 45 2250D BOS 1429/1429    CLT 1657/1657    AA    2.28   1.42X                   −− −− −− −− −− −− −−\n",
            ),
            expected_state="flight_deadhead",
            data={
                "dutyperiod": "1",
                "day_of_sequence": "1/1",
                "equipment_code": "45",
                "flight_number": "2250",
                "deadhead": "D",
                "departure_city": "BOS",
                "departure_local": "1429",
                "departure_home": "1429",
                "arrival_city": "CLT",
                "arrival_local": "1657",
                "arrival_home": "1657",
                "deadhead_block": "AA",
                "synth": "2.28",
                "ground": "1.42",
                "equipment_change": "X",
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
        ),
    ]

    _parse_test(tests, pbs_parser.FlightDeadheadLine)


def test_release_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "1",
                __name__,
                "                                 RLS 0054/0054   6.05   0.00   6.05  10.18        9.48 −− −− −−",
            ),
            expected_state="release",
            data={
                "release_local": "0054",
                "release_home": "0054",
                "block": "6.05",
                "synth": "0.00",
                "total_pay": "6.05",
                "duty": "10.18",
                "flight_duty": "9.48",
                "calendar_entries": ["−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                __name__,
                "                                 RLS 2203/2203   3.00   0.49   3.49   7.38        7.08",
            ),
            expected_state="release",
            data={
                "release_local": "2203",
                "release_home": "2203",
                "block": "3.00",
                "synth": "0.49",
                "total_pay": "3.49",
                "duty": "7.38",
                "flight_duty": "7.08",
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                __name__,
                "                                 RLS 0825/0325   7.15   0.00   7.15   8.45        8.15 16 −− 18 −− −− −− −−",
            ),
            expected_state="release",
            data={
                "release_local": "0825",
                "release_home": "0325",
                "block": "7.15",
                "synth": "0.00",
                "total_pay": "7.15",
                "duty": "8.45",
                "flight_duty": "8.15",
                "calendar_entries": ["16", "−−", "18", "−−", "−−", "−−", "−−"],
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
                __name__,
                "                LHR HI HIGH STREET                          442073684023   23.50       −− −− 25 −− −− −− −−",
            ),
            expected_state="hotel",
            data={
                "layover_city": "LHR",
                "hotel": "HI HIGH STREET",
                "hotel_phone": "442073684023",
                "rest": "23.50",
                "calendar_entries": ["−−", "−−", "25", "−−", "−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                __name__,
                "                ATH HOTEL INFO IN CCI/CREW PORTAL                          25.10       −− −− −− −− −− −− −−",
            ),
            expected_state="hotel",
            data={
                "layover_city": "ATH",
                "hotel": "HOTEL INFO IN CCI/CREW PORTAL",
                "hotel_phone": None,
                "rest": "25.10",
                "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                __name__,
                "                BDL SHERATON SPRINGFIELD MONARCH PLACE HOTE 14137811010    21.02",
            ),
            expected_state="hotel",
            data={
                "layover_city": "BDL",
                "hotel": "SHERATON SPRINGFIELD MONARCH PLACE HOTE",
                "hotel_phone": "14137811010",
                "rest": "21.02",
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "4",
                __name__,
                "                    STL MARRIOTT GRAND ST. LOUIS                13146219600    30.39\n",
            ),
            expected_state="hotel",
            data={
                "layover_city": "STL",
                "hotel": "MARRIOTT GRAND ST. LOUIS",
                "hotel_phone": "13146219600",
                "rest": "30.39",
                "calendar_entries": [],
            },
        ),
        # ParseTest(
        #     chunk=Chunk(
        #         "5",
        #         __name__,
        #         "                    LIMOTOUR MONTRÃ©AL                      5148758715\n",
        #     ),
        #     expected_state="hotel",
        #     data={
        #         "layover_city": "STL",
        #         "hotel": "MARRIOTT GRAND ST. LOUIS",
        #         "hotel_phone": "13146219600",
        #         "rest": "30.39",
        #         "calendar_entries": [],
        #     },
        # ),
    ]
    # TODO testing....

    _parse_test(tests, pbs_parser.HotelLine)


def test_unicode():
    pass


def test_additional_hotel_line(caplog):
    caplog.set_level(logging.INFO)
    tests = [
        ParseTest(
            chunk=Chunk(
                "4",
                __name__,
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
                __name__,
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
                __name__,
                "                    TRANS INFO IN CCI/CREW PORTAL                                      −− −−  1",
            ),
            expected_state="transportation",
            data={
                "transportation": "TRANS INFO IN CCI/CREW PORTAL",
                "transportation_phone": [],
                "calendar_entries": ["−−", "−−", "1"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                __name__,
                "                    SHUTTLE",
            ),
            expected_state="transportation",
            data={
                "transportation": "SHUTTLE",
                "transportation_phone": [],
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "4",
                __name__,
                "                    J & G’S CITYWIDE EXPRESS                5127868131",
            ),
            expected_state="transportation",
            data={
                "transportation": "J & G’S CITYWIDE EXPRESS",
                "transportation_phone": ["5127868131"],
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
                __name__,
                "TTL                                             15.47   0.37  16.24        57.26",
            ),
            expected_state="total",
            data={
                "block": "15.47",
                "synth": "0.37",
                "total_pay": "16.24",
                "tafb": "57.26",
                "calendar_entries": [],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "2",
                __name__,
                "TTL                                              4.58   0.17   5.15         7.18       −− −− −−",
            ),
            expected_state="total",
            data={
                "block": "4.58",
                "synth": "0.17",
                "total_pay": "5.15",
                "tafb": "7.18",
                "calendar_entries": ["−−", "−−", "−−"],
            },
        ),
        ParseTest(
            chunk=Chunk(
                "3",
                __name__,
                "TTL                                              4.54   0.21   5.15         7.16       30 −−  1",
            ),
            expected_state="total",
            data={
                "block": "4.54",
                "synth": "0.21",
                "total_pay": "5.15",
                "tafb": "7.16",
                "calendar_entries": ["30", "−−", "1"],
            },
        ),
    ]
    _parse_test(tests, pbs_parser.TotalLine)
