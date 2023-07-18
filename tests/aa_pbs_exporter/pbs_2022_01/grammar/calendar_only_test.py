from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="                                                                                       −− 17 18 19 20 21 22",
        result={"calendar_entries": ["−−", "17", "18", "19", "20", "21", "22"]},
    ),
    GrammarTest(
        txt="                                                                                       23 24 25 26 27 28 29",
        result={"calendar_entries": ["23", "24", "25", "26", "27", "28", "29"]},
    ),
]
parser = grammar.CalendarOnly


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
