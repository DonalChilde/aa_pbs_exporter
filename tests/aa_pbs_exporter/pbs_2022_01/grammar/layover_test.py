from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
        result={
            "layover_city": "MIA",
            "hotel": "SONESTA MIAMI AIRPORT",
            "hotel_phone": "13054469000",
            "rest": "11.27",
            "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
        },
    ),
    GrammarTest(
        txt="                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
        result={
            "layover_city": "LHR",
            "hotel": "PARK PLAZA WESTMINSTER BRIDGE LONDON",
            "hotel_phone": "443334006112",
            "rest": "24.00",
            "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
        },
    ),
    GrammarTest(
        txt="                JFK HOTEL INFO IN CCI/CREW PORTAL                          19.37",
        result={
            "layover_city": "JFK",
            "hotel": "HOTEL INFO IN CCI/CREW PORTAL",
            "rest": "19.37",
            "calendar_entries": [],
        },
    ),
    GrammarTest(
        txt="                JFK HOTEL INFO IN CCI/CREW PORTAL                          19.37 −− −− −− −− −− −− −−",
        result={
            "layover_city": "JFK",
            "hotel": "HOTEL INFO IN CCI/CREW PORTAL",
            "rest": "19.37",
            "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
        },
    ),
]
parser = grammar.Layover


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
