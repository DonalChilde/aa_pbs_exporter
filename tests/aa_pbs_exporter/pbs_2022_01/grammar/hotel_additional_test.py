from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="               +PHL MARRIOTT OLD CITY                       12152386000",
        result={
            "layover_city": "PHL",
            "hotel": "MARRIOTT OLD CITY",
            "hotel_phone": "12152386000",
            "calendar_entries": [],
        },
    ),
    GrammarTest(
        txt="               +PHL CAMBRIA HOTEL AND SUITES                12157325500 −− −− −− −− −− −− −−",
        result={
            "layover_city": "PHL",
            "hotel": "CAMBRIA HOTEL AND SUITES",
            "hotel_phone": "12157325500",
            "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
        },
    ),
    GrammarTest(
        txt="               +PHL NO PHONE NO CALENDAR                ",
        result={"layover_city": "PHL", "hotel": "NO PHONE NO CALENDAR"},
    ),
    GrammarTest(
        txt="               +PHL NO PHONE, WITH CALENDAR                −− −− −− −− −− −− −−",
        result={
            "layover_city": "PHL",
            "hotel": "NO PHONE, WITH CALENDAR",
            "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
        },
    ),
]
parser = grammar.HotelAdditional


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
