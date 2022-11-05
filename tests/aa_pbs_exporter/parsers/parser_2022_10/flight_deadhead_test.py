from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser

test_data = [
    lines.Flight(
        source=lines.SourceText(
            1,
            "4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31",
        ),
        dutyperiod_index="4",
        d_a="4/4",
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
        source=lines.SourceText(
            1,
            "2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X",
        ),
        dutyperiod_index="2",
        d_a="2/2",
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


def test_flight_deadhead():
    ctx = ParseContextTest("None")
    expected_state = "flight"
    parser = line_parser.FlightDeadhead()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
