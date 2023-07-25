from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import parsers as parsers
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from tests.aa_pbs_exporter.resources.helpers_3 import ParserTest2


Items = [
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=0,
            txt="                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−",
        ),
        result={
            "parse_ident": "DutyPeriodRelease",
            "parsed_data": {
                "release": "0739/0439",
                "block": "4.49",
                "synth": "0.00",
                "total_pay": "4.49",
                "duty": "6.19",
                "flight_duty": "5.49",
                "calendar": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
            "source": {
                "idx": 0,
                "txt": "                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00",
        ),
        result={
            "parse_ident": "DutyPeriodRelease",
            "parsed_data": {
                "release": "2252/2252",
                "block": "0.00",
                "synth": "5.46",
                "total_pay": "5.46",
                "duty": "6.46",
                "flight_duty": "0.00",
                "calendar": [],
            },
            "source": {
                "idx": 1,
                "txt": "                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00",
            },
        },
    ),
]
parser = parsers.DutyPeriodRelease()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")

    assert parse_result == test_data.result
