from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−",
        result={
            "release_time": "0739/0439",
            "block": "4.49",
            "synth": "0.00",
            "total_pay": "4.49",
            "duty": "6.19",
            "flight_duty": "5.49",
            "calendar_entries": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
        },
    ),
    GrammarTest(
        txt="                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00",
        result={
            "release_time": "2252/2252",
            "block": "0.00",
            "synth": "5.46",
            "total_pay": "5.46",
            "duty": "6.46",
            "flight_duty": "0.00",
            "calendar_entries": [],
        },
    ),
]
parser = grammar.DutyPeriodRelease


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
