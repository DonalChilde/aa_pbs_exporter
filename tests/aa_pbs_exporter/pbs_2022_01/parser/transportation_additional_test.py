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
            txt="                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
        ),
        result={
            "parse_ident": "TransportationAdditional",
            "parsed_data": {
                "name": ["SKY TRANSPORTATION SERVICE, LLC"],
                "phone": "",
                "calendar": [],
            },
            "source": {
                "idx": 0,
                "txt": "                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="                    DESERT COACH                            6022866161                    ",
        ),
        result={
            "parse_ident": "TransportationAdditional",
            "parsed_data": {"name": ["DESERT COACH"], "phone": "", "calendar": []},
            "source": {
                "idx": 1,
                "txt": "                    DESERT COACH                            6022866161                    ",
            },
        },
    ),
]
parser = parsers.TransportationAdditional()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")
    assert parse_result == test_data.result
