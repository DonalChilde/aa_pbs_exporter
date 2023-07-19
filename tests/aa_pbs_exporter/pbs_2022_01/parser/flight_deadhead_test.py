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
            txt="3  3/3 CE 2308D DFW 1635/1635    AUS 1741/1741    AA    1.06                                                ",
        ),
        result={
            "parse_ident": "Flight",
            "parsed_data": {
                "dutyperiod_idx": "3",
                "dep_arr_day": "3/3",
                "eq_code": "CE",
                "flight_number": "2308",
                "deadhead": "D",
                "departure_station": "DFW",
                "departure_time": "1635/1635",
                "meal": "",
                "arrival_station": "AUS",
                "arrival_time": "1741/1741",
                "block": "0.00",
                "synth": "1.06",
                "ground": "0.00",
                "equipment_change": "",
                "calendar": [],
            },
            "source": {
                "idx": 0,
                "txt": "3  3/3 CE 2308D DFW 1635/1635    AUS 1741/1741    AA    1.06                                                ",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X",
        ),
        result={
            "parse_ident": "Flight",
            "parsed_data": {
                "dutyperiod_idx": "2",
                "dep_arr_day": "2/2",
                "eq_code": "45",
                "flight_number": "1614",
                "deadhead": "D",
                "departure_station": "MCI",
                "departure_time": "1607/1407",
                "meal": "",
                "arrival_station": "DFW",
                "arrival_time": "1800/1600",
                "block": "0.00",
                "synth": "1.53",
                "ground": "1.27",
                "equipment_change": "X",
                "calendar": [],
            },
            "source": {
                "idx": 1,
                "txt": "2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=2,
            txt="4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31",
        ),
        result={
            "parse_ident": "Flight",
            "parsed_data": {
                "dutyperiod_idx": "4",
                "dep_arr_day": "4/4",
                "eq_code": "64",
                "flight_number": "2578",
                "deadhead": "D",
                "departure_station": "MIA",
                "departure_time": "1949/1649",
                "meal": "",
                "arrival_station": "SAN",
                "arrival_time": "2220/2220",
                "block": "0.00",
                "synth": "5.31",
                "ground": "0.00",
                "equipment_change": "",
                "calendar": [],
            },
            "source": {
                "idx": 2,
                "txt": "4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31",
            },
        },
    ),
]
parser = parsers.FlightDeadhead()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")

    assert parse_result == test_data.result
