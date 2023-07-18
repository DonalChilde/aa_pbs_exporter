from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="SEQ 25064   1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU",
        result={
            "number": "25064",
            "ops_count": "1",
            "positions": ["CA", "FO"],
            "operations": [],
            "qualifications": [],
        },
    ),
    GrammarTest(
        txt="SEQ 6292    1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU",
        result={
            "number": "6292",
            "ops_count": "1",
            "positions": ["CA", "FO"],
            "operations": ["SPANISH"],
            "qualifications": [],
        },
    ),
    GrammarTest(
        txt="SEQ 16945   1 OPS   POSN CA FO                SPECIAL QUALIFICATION                    MO TU WE TH FR SA SU",
        result={
            "number": "16945",
            "ops_count": "1",
            "positions": ["CA", "FO"],
            "operations": [],
            "qualifications": ["SPECIAL"],
        },
    ),
    GrammarTest(
        txt="SEQ 25018   2 OPS   POSN CA FO                MEXICO QUALIFICATION                     MO TU WE TH FR SA SU",
        result={
            "number": "25018",
            "ops_count": "2",
            "positions": ["CA", "FO"],
            "operations": [],
            "qualifications": ["MEXICO"],
        },
    ),
    GrammarTest(
        txt="SEQ 30569   1 OPS   POSN CA FO                                                         New prior month",
        result={
            "number": "30569",
            "ops_count": "1",
            "positions": ["CA", "FO"],
            "operations": [],
            "qualifications": [],
        },
    ),
    GrammarTest(
        txt="SEQ 30890   1 OPS   POSN CA FO                                                         Replaces prior month",
        result={
            "number": "30890",
            "ops_count": "1",
            "positions": ["CA", "FO"],
            "operations": [],
            "qualifications": [],
        },
    ),
    GrammarTest(
        txt="SEQ 19448   1 OPS   POSN CA FO                ST. THOMAS OPERATION                     MO TU WE TH FR SA SU ",
        result={
            "number": "19448",
            "ops_count": "1",
            "positions": ["CA", "FO"],
            "operations": ["ST.", "THOMAS"],
            "qualifications": [],
        },
    ),
    GrammarTest(
        txt="SEQ 265    10 OPS   POSN FB ONLY              GERMAN   OPERATION                       MO TU WE TH FR SA SU ",
        result={
            "number": "265",
            "ops_count": "10",
            "positions": ["FB"],
            "operations": ["GERMAN"],
            "qualifications": [],
        },
    ),
    GrammarTest(
        txt="SEQ 264     4 OPS   POSN FB ONLY                                                       MO TU WE TH FR SA SU ",
        result={
            "number": "264",
            "ops_count": "4",
            "positions": ["FB"],
            "operations": [],
            "qualifications": [],
        },
    ),
    GrammarTest(
        txt="SEQ 657     2 OPS   POSN FO C                                                          MO TU WE TH FR SA SU ",
        result={
            "number": "657",
            "ops_count": "2",
            "positions": ["FO", "C"],
            "operations": [],
            "qualifications": [],
        },
    ),
    GrammarTest(
        txt="SEQ 30097   1 OPS   POSN FB ONLY              JAPANESE OPERATION                       Replaces prior month ",
        result={
            "number": "30097",
            "ops_count": "1",
            "positions": ["FB"],
            "operations": ["JAPANESE"],
            "qualifications": [],
        },
    ),
]
parser = grammar.TripHeader


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
