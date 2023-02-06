from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import HotelAdditional, IndexedString
from aa_pbs_exporter.pbs_2022_01.parse import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="hotel_additional_1",
        txt="               +PHL MARRIOTT OLD CITY                       12152386000",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="hotel_additional_2",
        txt="               +PHL CAMBRIA HOTEL AND SUITES                12157325500",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "hotel_additional_1": ParseResult(
        current_state="hotel_additional",
        parsed_data=HotelAdditional(
            source=IndexedString(
                idx=1,
                txt="               +PHL MARRIOTT OLD CITY                       12152386000",
            ),
            layover_city="PHL",
            name="MARRIOTT OLD CITY",
            phone="12152386000",
            calendar="",
        ),
    ),
    "hotel_additional_2": ParseResult(
        current_state="hotel_additional",
        parsed_data=HotelAdditional(
            source=IndexedString(
                idx=2,
                txt="               +PHL CAMBRIA HOTEL AND SUITES                12157325500",
            ),
            layover_city="PHL",
            name="CAMBRIA HOTEL AND SUITES",
            phone="12157325500",
            calendar="",
        ),
    ),
}


PARSER = line_parser.HotelAdditional()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "hotel_additional"
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
