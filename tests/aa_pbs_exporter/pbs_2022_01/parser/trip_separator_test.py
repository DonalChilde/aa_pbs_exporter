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
            txt="−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
        ),
        result={
            "parse_ident": "TripSeparator",
            "parsed_data": {},
            "source": {
                "idx": 0,
                "txt": "−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
            },
        },
    ),
]
parser = parsers.TripSeparator()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")

    assert parse_result == test_data.result
