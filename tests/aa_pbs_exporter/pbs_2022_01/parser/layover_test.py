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
            txt="                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
        ),
        result={
            "parse_ident": "Layover",
            "parsed_data": {
                "layover_city": "MIA",
                "name": "SONESTA MIAMI AIRPORT",
                "phone": "13054469000",
                "rest": "11.27",
                "calendar": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
            "source": {
                "idx": 0,
                "txt": "                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
        ),
        result={
            "parse_ident": "Layover",
            "parsed_data": {
                "layover_city": "LHR",
                "name": "PARK PLAZA WESTMINSTER BRIDGE LONDON",
                "phone": "443334006112",
                "rest": "24.00",
                "calendar": ["−−", "−−", "−−", "−−", "−−", "−−", "−−"],
            },
            "source": {
                "idx": 1,
                "txt": "                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=2,
            txt="                JFK HOTEL INFO IN CCI/CREW PORTAL                          19.37\n",
        ),
        result={
            "parse_ident": "Layover",
            "parsed_data": {
                "layover_city": "JFK",
                "name": "HOTEL INFO IN CCI/CREW PORTAL",
                "phone": "",
                "rest": "19.37",
                "calendar": [],
            },
            "source": {
                "idx": 2,
                "txt": "                JFK HOTEL INFO IN CCI/CREW PORTAL                          19.37\n",
            },
        },
    ),
]
parser = parsers.Layover()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")
    assert parse_result == test_data.result
