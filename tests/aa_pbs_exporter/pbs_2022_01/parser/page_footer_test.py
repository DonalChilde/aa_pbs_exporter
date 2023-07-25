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
            txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 737  DOM                              PAGE   644",
        ),
        result={
            "parse_ident": "PageFooter",
            "parsed_data": {
                "issued": "08APR2022",
                "effective": "02MAY2022",
                "base": "LAX",
                "satelite_base": "",
                "equipment": "737",
                "division": "DOM",
                "page": "644",
            },
            "source": {
                "idx": 0,
                "txt": "COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 737  DOM                              PAGE   644",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 320  INTL                             PAGE  1178",
        ),
        result={
            "parse_ident": "PageFooter",
            "parsed_data": {
                "issued": "08APR2022",
                "effective": "02MAY2022",
                "base": "LAX",
                "satelite_base": "",
                "equipment": "320",
                "division": "INTL",
                "page": "1178",
            },
            "source": {
                "idx": 1,
                "txt": "COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 320  INTL                             PAGE  1178",
            },
        },
    ),
]
parser = parsers.PageFooter()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")
    assert parse_result == test_data.result
