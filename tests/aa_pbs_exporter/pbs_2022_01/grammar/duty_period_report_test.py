from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="                RPT 1237/1237                                                           2 −− −− −− −− −− −−",
        result={
            "report": "1237/1237",
            "calendar_entries": ["2", "−−", "−−", "−−", "−−", "−−", "−−"],
        },
    ),
    GrammarTest(
        txt="                RPT 1000/1000                                                          sequence 25384/30DEC",
        result={
            "report": "1000/1000",
            "calendar_entries": [],
            "sequence_number": "25384",
            "date": ["30", "DEC"],
        },
    ),
    GrammarTest(
        txt="                RPT 1829/1829                                                          sequence 01JUL",
        result={"report": "1829/1829", "calendar_entries": [], "date": ["01", "JUL"]},
    ),
]
parser = grammar.DutyPeriodReport


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
