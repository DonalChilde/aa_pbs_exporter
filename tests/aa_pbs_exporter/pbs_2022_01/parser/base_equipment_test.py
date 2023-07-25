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
            txt="BOS 737",
        ),
        result={
            "parse_ident": "BaseEquipment",
            "parsed_data": {"base": "BOS", "satellite_base": "", "equipment": "737"},
            "source": {"idx": 0, "txt": "BOS 737"},
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="LAX SAN 737",
        ),
        result={
            "parse_ident": "BaseEquipment",
            "parsed_data": {"base": "LAX", "satellite_base": "SAN", "equipment": "737"},
            "source": {"idx": 1, "txt": "LAX SAN 737"},
        },
    ),
]
parser = parsers.BaseEquipment()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")

    assert parse_result == test_data.result
