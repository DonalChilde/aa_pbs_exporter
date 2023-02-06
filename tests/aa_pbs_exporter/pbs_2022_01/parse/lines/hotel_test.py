from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import Hotel, IndexedString
from aa_pbs_exporter.pbs_2022_01.parse import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="hotel_1",
        txt="                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="hotel_2",
        txt="                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "hotel_1": ParseResult(
        current_state="hotel",
        parsed_data=Hotel(
            source=IndexedString(
                idx=1,
                txt="                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
            ),
            layover_city="MIA",
            name="SONESTA MIAMI AIRPORT",
            phone="13054469000",
            rest="11.27",
            calendar="−− −− −− −− −− −− −−",
        ),
    ),
    "hotel_2": ParseResult(
        current_state="hotel",
        parsed_data=Hotel(
            source=IndexedString(
                idx=2,
                txt="                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
            ),
            layover_city="LHR",
            name="PARK PLAZA WESTMINSTER BRIDGE LONDON",
            phone="443334006112",
            rest="24.00",
            calendar="−− −− −− −− −− −− −−",
        ),
    ),
}


PARSER = line_parser.Hotel()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "hotel"
    parse_lines(
        test_data=test_data,
        result_data=result_data,
        parser=PARSER,
        output_path=outpath,
        # skip_test=True,
    )


def test_parse_fail():
    with pytest.raises(ParseException):
        PARSER.parse(IndexedString(idx=1, txt="foo"), ctx={})
