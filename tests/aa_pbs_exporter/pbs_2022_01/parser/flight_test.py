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
            txt="1  1/1 65 2131  SAN 1337/1337    ORD 1935/1735   3.58          1.10X                   −− −− −− −− −− −− −−",
        ),
        result={
            "parse_ident": "Flight",
            "parsed_data": {
                "dutyperiod_idx": "1",
                "dep_arr_day": "1/1",
                "eq_code": "65",
                "flight_number": "2131",
                "deadhead": "",
                "departure_station": "SAN",
                "departure_time": "1337/1337",
                "meal": "",
                "arrival_station": "ORD",
                "arrival_time": "1935/1735",
                "block": "3.58",
                "synth": "0.00",
                "ground": "1.10",
                "equipment_change": "X",
                "calendar": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
            "source": {
                "idx": 0,
                "txt": "1  1/1 65 2131  SAN 1337/1337    ORD 1935/1735   3.58          1.10X                   −− −− −− −− −− −− −−",
            },
        },
    ),
]
parser = parsers.Flight()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")

    assert parse_result == test_data.result
