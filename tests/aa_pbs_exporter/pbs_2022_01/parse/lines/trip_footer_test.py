from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parse_v2 as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import IndexedString, TripFooter
from aa_pbs_exporter.pbs_2022_01.parse_v2 import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="trip_footer_1",
        txt="TTL                                              7.50   0.00   7.50        10.20       −− −− −−",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="trip_footer_2",
        txt="TTL                                             17.18   0.00  17.18        60.04",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "trip_footer_1": ParseResult(
        current_state="trip_footer",
        parsed_data=TripFooter(
            source=IndexedString(
                idx=1,
                txt="TTL                                              7.50   0.00   7.50        10.20       −− −− −−",
            ),
            block="7.50",
            synth="0.00",
            total_pay="7.50",
            tafb="10.20",
            calendar="−− −− −−",
        ),
    ),
    "trip_footer_2": ParseResult(
        current_state="trip_footer",
        parsed_data=TripFooter(
            source=IndexedString(
                idx=2,
                txt="TTL                                             17.18   0.00  17.18        60.04",
            ),
            block="17.18",
            synth="0.00",
            total_pay="17.18",
            tafb="60.04",
            calendar="",
        ),
    ),
}


PARSER = line_parser.TripFooter()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "trip_footer"
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
