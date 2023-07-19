from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="                    SIN FIN DE SERVICIOS                    3331223240",
        result={
            "transportation": "SIN FIN DE SERVICIOS",
            "phone": "3331223240",
            "calendar_entries": [],
        },
    ),
    GrammarTest(
        txt="                    VIP TRANSPORTATION− OGG                 8088712702                 −− −− −−",
        result={
            "transportation": "VIP TRANSPORTATION− OGG",
            "phone": "8088712702",
            "calendar_entries": ["−−", "−−", "−−"],
        },
    ),
    GrammarTest(
        txt="                    This test has no phone number, but has a calendar                                  −− −− −−",
        result={
            "transportation": "This test has no phone number, but has a calendar",
            "calendar_entries": ["−−", "−−", "−−"],
        },
    ),
    GrammarTest(
        txt="                    TRANS INFO IN CCI/CREW PORTAL",
        result={"transportation": "TRANS INFO IN CCI/CREW PORTAL"},
    ),
]
parser = grammar.Transportation


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
