# # pylint: disable=missing-docstring

# import logging
# from dataclasses import dataclass, field
# from typing import Dict

# from pfmsoft.text_chunk_parser import (
#     Chunk,
#     ChunkParser,
#     FailedParseException,
#     ParseResult,
# )
# from pfmsoft.text_chunk_parser.enumerated_filtered_iterator import Enumerated

# from aa_pbs_exporter.pilot_pbs_2022 import parser_2 as pbs_parser


# # pylint: disable=missing-function-docstring
# # pylint: disable=line-too-long
# @dataclass
# class ParseTest:
#     chunk: Chunk
#     expected_state: str
#     data: Dict = field(default_factory=dict)


# def parse_test(chunk: Chunk, expected_state: str, data: Dict, parser: ChunkParser):
#     try:
#         parse_result: ParseResult = parser().parse(chunk, None, None)
#     except FailedParseException as exc:
#         print(exc.__context__.explain())  # pylint: disable=no-member
#         assert False
#     print("Data:\n", parse_result.data)
#     assert parse_result.new_state == expected_state
#     assert parse_result.data == data


# def test_footer(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               PHL 787  INTL                             PAGE  1990",
#     )
#     data = {
#         "issued": "08APR2022",
#         "effective": "02MAY2022",
#         "base": "PHL",
#         "equipment": "787",
#         "division": "INTL",
#         "internal_page": "1990",
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "footer", data, pbs_parser.FooterLine)


# def test_first_header(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/",
#     )
#     data = {}
#     chunk = Chunk(value)
#     parse_test(chunk, "first_header", data, pbs_parser.FirstHeaderLine)


# def test_second_header(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01",
#     )
#     data = {
#         "calendar_from": {"month": "05", "day": "02"},
#         "calendar_to": {"month": "06", "day": "01"},
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "second_header", data, pbs_parser.SecondHeaderLine)


# def test_dash_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
#     )
#     data = {}
#     chunk = Chunk(value)
#     parse_test(chunk, "dash_line", data, pbs_parser.DashLine)


# def test_base_equipment_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "PHL 787",
#     )
#     data = {"base": "PHL", "equipment": "787"}
#     chunk = Chunk(value)
#     parse_test(chunk, "base_equipment", data, pbs_parser.BaseEquipmentLine)


# def test_sequence_header_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "SEQ 1313   28 OPS   POSN CA FO                GREEK OPERATION                          MO TU WE TH FR SA SU ",
#     )
#     data = {
#         "sequence": "1313",
#         "ops_count": "28",
#         "positions": ["CA", "FO"],
#         "operations": ["GREEK"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "sequence_header", data, pbs_parser.SequenceHeaderLine)

#     value = Enumerated(
#         1,
#         "SEQ 30533   1 OPS   POSN CA FO                                                         Replaces prior month",
#     )
#     data = {
#         "sequence": "30533",
#         "ops_count": "1",
#         "positions": ["CA", "FO"],
#         "operations": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "sequence_header", data, pbs_parser.SequenceHeaderLine)


# def test_report_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "                RPT 0800/0800                                                          −− −− −− −− −−  7 −−",
#     )
#     data = {
#         "report_local": "0800",
#         "report_home": "0800",
#         "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "7", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "report", data, pbs_parser.ReportLine)

#     value = Enumerated(
#         1,
#         "                RPT 1545/1545                                                          −− −− −− −− −− −− −−",
#     )
#     data = {
#         "report_local": "1545",
#         "report_home": "1545",
#         "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "report", data, pbs_parser.ReportLine)

#     value = Enumerated(
#         1,
#         "                RPT 0652/0652",
#     )
#     data = {
#         "report_local": "0652",
#         "report_home": "0652",
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "report", data, pbs_parser.ReportLine)

#     value = Enumerated(
#         1,
#         "                RPT 0730/0730                                                          sequence 5144/30APR",
#     )
#     data = {
#         "report_local": "0730",
#         "report_home": "0730",
#         "calendar_entries": [],
#         "sequence_number": "5144",
#         "date": ["30", "APR"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "report", data, pbs_parser.ReportLine)


# def test_flight_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "2  2/2 26 2112  DFW 0600/0700  B LAX 0725/1025   3.25          2.35X",
#     )
#     data = {
#         "dutyperiod": "2",
#         "day_of_sequence": "2/2",
#         "equipment_code": "26",
#         "flight_number": "2112",
#         "departure_city": "DFW",
#         "departure_local": "0600",
#         "departure_home": "0700",
#         "crew_meal": "B",
#         "arrival_city": "LAX",
#         "arrival_local": "0725",
#         "arrival_home": "1025",
#         "block": "3.25",
#         "ground": "2.35",
#         "equipment_change": "X",
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "flight", data, pbs_parser.FlightLine)

#     value = Enumerated(
#         1,
#         "1  1/1 64  508  MBJ 1306/1406    DFW 1700/1800   3.54                                  −− −− −− −− −− −− −−",
#     )
#     data = {
#         "dutyperiod": "1",
#         "day_of_sequence": "1/1",
#         "equipment_code": "64",
#         "flight_number": "508",
#         "departure_city": "MBJ",
#         "departure_local": "1306",
#         "departure_home": "1406",
#         "crew_meal": "",
#         "arrival_city": "DFW",
#         "arrival_local": "1700",
#         "arrival_home": "1800",
#         "block": "3.54",
#         "ground": "0.00",
#         "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "flight", data, pbs_parser.FlightLine)


# def test_flight_deadhead_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "1  1/1 45  435D MIA 1010/1010    CLT 1225/1225    AA    2.15                           −− −− −− −− −− −− −−\n",
#     )
#     data = {
#         "dutyperiod": "1",
#         "day_of_sequence": "1/1",
#         "equipment_code": "45",
#         "flight_number": "435",
#         "deadhead": "D",
#         "departure_city": "MIA",
#         "departure_local": "1010",
#         "departure_home": "1010",
#         "crew_meal": "",
#         "arrival_city": "CLT",
#         "arrival_local": "1225",
#         "arrival_home": "1225",
#         "deadhead_block": "AA",
#         "ground": "0.00",
#         "synth": "2.15",
#         "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "flight_deadhead", data, pbs_parser.FlightDeadheadLine)

#     value = Enumerated(
#         1,
#         "1  1/1 45 2250D BOS 1429/1429    CLT 1657/1657    AA    2.28   1.42X                   −− −− −− −− −− −− −−\n",
#     )
#     data = {
#         "dutyperiod": "1",
#         "day_of_sequence": "1/1",
#         "equipment_code": "45",
#         "flight_number": "2250",
#         "deadhead": "D",
#         "departure_city": "BOS",
#         "departure_local": "1429",
#         "departure_home": "1429",
#         "crew_meal": "",
#         "arrival_city": "CLT",
#         "arrival_local": "1657",
#         "arrival_home": "1657",
#         "deadhead_block": "AA",
#         "synth": "2.28",
#         "ground": "1.42",
#         "equipment_change": "X",
#         "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "flight_deadhead", data, pbs_parser.FlightDeadheadLine)


# def test_release_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "                                 RLS 0054/0054   6.05   0.00   6.05  10.18        9.48 −− −− −−",
#     )
#     data = {
#         "release_local": "0054",
#         "release_home": "0054",
#         "block": "6.05",
#         "synth": "0.00",
#         "total_pay": "6.05",
#         "duty": "10.18",
#         "flight_duty": "9.48",
#         "calendar_entries": ["−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "release", data, pbs_parser.ReleaseLine)

#     value = Enumerated(
#         1,
#         "                                 RLS 2203/2203   3.00   0.49   3.49   7.38        7.08",
#     )
#     data = {
#         "release_local": "2203",
#         "release_home": "2203",
#         "block": "3.00",
#         "synth": "0.49",
#         "total_pay": "3.49",
#         "duty": "7.38",
#         "flight_duty": "7.08",
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "release", data, pbs_parser.ReleaseLine)

#     value = Enumerated(
#         1,
#         "                                 RLS 0825/0325   7.15   0.00   7.15   8.45        8.15 16 −− 18 −− −− −− −−",
#     )
#     data = {
#         "release_local": "0825",
#         "release_home": "0325",
#         "block": "7.15",
#         "synth": "0.00",
#         "total_pay": "7.15",
#         "duty": "8.45",
#         "flight_duty": "8.15",
#         "calendar_entries": ["16", "−−", "18", "−−", "−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "release", data, pbs_parser.ReleaseLine)


# def test_hotel_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "                LHR HI HIGH STREET                          442073684023   23.50       −− −− 25 −− −− −− −−",
#     )
#     data = {
#         "layover_city": "LHR",
#         "hotel": "HI HIGH STREET",
#         "hotel_phone": "442073684023",
#         "rest": "23.50",
#         "calendar_entries": ["−−", "−−", "25", "−−", "−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "hotel", data, pbs_parser.HotelLine)

#     value = Enumerated(
#         1,
#         "                ATH HOTEL INFO IN CCI/CREW PORTAL                          25.10       −− −− −− −− −− −− −−",
#     )
#     data = {
#         "layover_city": "ATH",
#         "hotel": "HOTEL INFO IN CCI/CREW PORTAL",
#         "hotel_phone": [],
#         "rest": "25.10",
#         "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "hotel", data, pbs_parser.HotelLine)

#     value = Enumerated(
#         1,
#         "                BDL SHERATON SPRINGFIELD MONARCH PLACE HOTE 14137811010    21.02",
#     )
#     data = {
#         "layover_city": "BDL",
#         "hotel": "SHERATON SPRINGFIELD MONARCH PLACE HOTE",
#         "hotel_phone": "14137811010",
#         "rest": "21.02",
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "hotel", data, pbs_parser.HotelLine)

#     value = Enumerated(
#         1,
#         "                    STL MARRIOTT GRAND ST. LOUIS                13146219600    30.39\n",
#     )
#     data = {
#         "layover_city": "STL",
#         "hotel": "MARRIOTT GRAND ST. LOUIS",
#         "hotel_phone": "13146219600",
#         "rest": "30.39",
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "hotel", data, pbs_parser.HotelLine)


# def test_unicode():
#     pass


# def test_additional_hotel_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "               +LAS THE WESTIN LAS VEGAS HOTEL              17028365900",
#     )
#     data = {
#         "layover_city": "LAS",
#         "hotel": "THE WESTIN LAS VEGAS HOTEL",
#         "hotel_phone": "17028365900",
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "additional_hotel", data, pbs_parser.AdditionalHotelLine)


# def test_transportation_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "                    COMET CAR HIRE (CCH) LTD                442088979984               −− −− −−",
#     )
#     data = {
#         "transportation": "COMET CAR HIRE (CCH) LTD",
#         "transportation_phone": ["442088979984"],
#         "calendar_entries": ["−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "transportation", data, pbs_parser.TransportationLine)

#     value = Enumerated(
#         1,
#         "                    TRANS INFO IN CCI/CREW PORTAL                                      −− −−  1",
#     )
#     data = {
#         "transportation": "TRANS INFO IN CCI/CREW PORTAL",
#         "transportation_phone": [],
#         "calendar_entries": ["−−", "−−", "1"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "transportation", data, pbs_parser.TransportationLine)

#     value = Enumerated(
#         1,
#         "                    SHUTTLE",
#     )
#     data = {
#         "transportation": "SHUTTLE",
#         "transportation_phone": [],
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "transportation", data, pbs_parser.TransportationLine)

#     value = Enumerated(
#         1,
#         "                    J & G’S CITYWIDE EXPRESS                5127868131",
#     )
#     data = {
#         "transportation": "J & G’S CITYWIDE EXPRESS",
#         "transportation_phone": ["5127868131"],
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "transportation", data, pbs_parser.TransportationLine)


# def test_total_line(caplog):
#     caplog.set_level(logging.INFO)
#     value = Enumerated(
#         1,
#         "TTL                                             15.47   0.37  16.24        57.26",
#     )
#     data = {
#         "block": "15.47",
#         "synth": "0.37",
#         "total_pay": "16.24",
#         "tafb": "57.26",
#         "calendar_entries": [],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "total", data, pbs_parser.TotalLine)

#     value = Enumerated(
#         1,
#         "TTL                                              4.58   0.17   5.15         7.18       −− −− −−",
#     )
#     data = {
#         "block": "4.58",
#         "synth": "0.17",
#         "total_pay": "5.15",
#         "tafb": "7.18",
#         "calendar_entries": ["−−", "−−", "−−"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "total", data, pbs_parser.TotalLine)

#     value = Enumerated(
#         1,
#         "TTL                                              4.54   0.21   5.15         7.16       30 −−  1",
#     )
#     data = {
#         "block": "4.54",
#         "synth": "0.21",
#         "total_pay": "5.15",
#         "tafb": "7.16",
#         "calendar_entries": ["30", "−−", "1"],
#     }
#     chunk = Chunk(value)
#     parse_test(chunk, "total", data, pbs_parser.TotalLine)
