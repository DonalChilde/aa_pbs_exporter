from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import parsers_g as parsers
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from tests.aa_pbs_exporter.resources.helpers_3 import ParserTest2


Items = [
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=0,
            txt="                RPT 1237/1237                                                           2 −− −− −− −− −− −−",
        ),
        result={
            "parse_ident": "DutyPeriodReport",
            "parsed_data": {
                "report": "1237/1237",
                "calendar": ["2", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
            "source": {
                "idx": 0,
                "txt": "                RPT 1237/1237                                                           2 −− −− −− −− −− −−",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="                RPT 1000/1000                                                          sequence 25384/30DEC",
        ),
        result={
            "parse_ident": "DutyPeriodReport",
            "parsed_data": {"report": "1000/1000", "calendar": []},
            "source": {
                "idx": 1,
                "txt": "                RPT 1000/1000                                                          sequence 25384/30DEC",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=2,
            txt="                RPT 1829/1829                                                          sequence 01JUL",
        ),
        result={
            "parse_ident": "DutyPeriodReport",
            "parsed_data": {"report": "1829/1829", "calendar": []},
            "source": {
                "idx": 2,
                "txt": "                RPT 1829/1829                                                          sequence 01JUL",
            },
        },
    ),
]
parser = parsers.DutyPeriodReport()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")

    assert parse_result == test_data.result
