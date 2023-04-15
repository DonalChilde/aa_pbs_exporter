from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parsers as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import (
    IndexedString,
    TransportationAdditional,
)
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="transportation_additional_1",
        txt="                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="transportation_additional_2",
        txt="                    DESERT COACH                            6022866161",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "transportation_additional_1": ParseResult(
        current_state="transportation_additional",
        parsed_data=TransportationAdditional(
            source=IndexedString(
                idx=1,
                txt="                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
            ),
            name="SKY TRANSPORTATION SERVICE, LLC",
            phone="8566169633",
            calendar="",
        ),
    ),
    "transportation_additional_2": ParseResult(
        current_state="transportation_additional",
        parsed_data=TransportationAdditional(
            source=IndexedString(
                idx=2,
                txt="                    DESERT COACH                            6022866161",
            ),
            name="DESERT COACH",
            phone="6022866161",
            calendar="",
        ),
    ),
}


PARSER = line_parser.TransportationAdditional()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "transportation_additional"
    parse_lines(
        test_data=test_data,
        result_data=result_data,
        parser=PARSER,
        output_path=outpath,
        # skip_test=True,
    )


def test_parse_fail():
    with pytest.raises(ParseException):
        PARSER.parse(IndexedString(idx=1, txt=""), ctx={})
