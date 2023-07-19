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
            txt="TTL                                              7.50   0.00   7.50        10.20       −− −− −−",
        ),
        result={
            "parse_ident": "TripFooter",
            "parsed_data": {
                "block": "7.50",
                "synth": "0.00",
                "total_pay": "7.50",
                "tafb": "10.20",
                "calendar": ["−−", "−−", "−−"],
            },
            "source": {
                "idx": 0,
                "txt": "TTL                                              7.50   0.00   7.50        10.20       −− −− −−",
            },
        },
    ),
]
parser = parsers.TripFooter()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")
    assert parse_result == test_data.result
