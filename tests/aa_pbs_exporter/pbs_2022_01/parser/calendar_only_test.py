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
            txt="                                                                                       −− 17 18 19 20 21 22",
        ),
        result={
            "parse_ident": "CalendarOnly",
            "parsed_data": {"calendar": ["−−", "17", "18", "19", "20", "21", "22"]},
            "source": {
                "idx": 0,
                "txt": "                                                                                       −− 17 18 19 20 21 22",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="                                                                                       23 24 25 26 27 28 29",
        ),
        result={
            "parse_ident": "CalendarOnly",
            "parsed_data": {"calendar": ["23", "24", "25", "26", "27", "28", "29"]},
            "source": {
                "idx": 1,
                "txt": "                                                                                       23 24 25 26 27 28 29",
            },
        },
    ),
]
parser = parsers.CalendarOnly()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")
    assert parse_result == test_data.result
