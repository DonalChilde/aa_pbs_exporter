from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.indexed_string import IndexedString

test_data = [
    lines.Flight(
        source=IndexedString(
            1,
            "1  1/1 65 2131  SAN 1337/1337    ORD 1935/1735   3.58          1.10X                   −− −− −− −− −− −− −−",
        ),
        dutyperiod_index="1",
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


def test_flight():
    ctx = ParseContextTest("None")
    expected_state = "flight"
    parser = line_parser.Flight()
    for data in test_data:
        state = parser.parse(data.source, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
