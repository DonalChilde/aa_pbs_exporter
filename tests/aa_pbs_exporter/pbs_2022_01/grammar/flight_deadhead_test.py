from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="3  3/3 CE 2308D DFW 1635/1635    AUS 1741/1741    AA    1.06                                                ",
        result={
            "dutyperiod": "3",
            "day_of_sequence": "3/3",
            "equipment_code": "CE",
            "flight_number": "2308",
            "deadhead": "D",
            "departure_station": "DFW",
            "departure_time": "1635/1635",
            "crew_meal": "",
            "arrival_station": "AUS",
            "arrival_time": "1741/1741",
            "deadhead_block": "AA",
            "synth": "1.06",
            "ground": "0.00",
            "equipment_change": "",
            "calendar_entries": [],
        },
    ),
    GrammarTest(
        txt="2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X",
        result={
            "dutyperiod": "2",
            "day_of_sequence": "2/2",
            "equipment_code": "45",
            "flight_number": "1614",
            "deadhead": "D",
            "departure_station": "MCI",
            "departure_time": "1607/1407",
            "crew_meal": "",
            "arrival_station": "DFW",
            "arrival_time": "1800/1600",
            "deadhead_block": "AA",
            "synth": "1.53",
            "ground": "1.27",
            "equipment_change": "X",
            "calendar_entries": [],
        },
    ),
    GrammarTest(
        txt="4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31",
        result={
            "dutyperiod": "4",
            "day_of_sequence": "4/4",
            "equipment_code": "64",
            "flight_number": "2578",
            "deadhead": "D",
            "departure_station": "MIA",
            "departure_time": "1949/1649",
            "crew_meal": "",
            "arrival_station": "SAN",
            "arrival_time": "2220/2220",
            "deadhead_block": "AA",
            "synth": "5.31",
            "ground": "0.00",
            "equipment_change": "",
            "calendar_entries": [],
        },
    ),
]
parser = grammar.FlightDeadhead


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
