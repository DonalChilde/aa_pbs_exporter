from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
        result={
            "transportation": "SKY TRANSPORTATION SERVICE, LLC",
            "phone": "8566169633",
            "calendar_entries": [],
        },
    ),
    GrammarTest(
        txt="                    DESERT COACH                            6022866161                    ",
        result={
            "transportation": "DESERT COACH",
            "phone": "6022866161",
            "calendar_entries": [],
        },
    ),
]
parser = grammar.TransportationAdditional


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
