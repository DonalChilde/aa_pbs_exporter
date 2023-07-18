from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest

Items = [
    GrammarTest(
        txt="1  1/1 65 2131  SAN 1337/1337    ORD 1935/1735   3.58          1.10X                   −− −− −− −− −− −− −−",
        result={
            "dutyperiod": "1",
            "day_of_sequence": "1/1",
            "equipment_code": "65",
            "flight_number": "2131",
            "departure_station": "SAN",
            "departure_time": "1337/1337",
            "crew_meal": "",
            "arrival_station": "ORD",
            "arrival_time": "1935/1735",
            "block": "3.58",
            "ground": "1.10",
            "equipment_change": "X",
            "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
        },
    )
]
parser = grammar.Flight


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{result!r}")
    assert result == test_data.result
