from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parsers as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import IndexedString, TripHeader
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_exception import (
    ParseException,
)

test_data = [
    ParseTestData(
        name="trip_header_1",
        txt="SEQ 25064   1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="trip_header_2",
        txt="SEQ 6292    1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU",
        description="A base equipment with satellite base",
    ),
    ParseTestData(
        name="trip_header_3",
        txt="SEQ 16945   1 OPS   POSN CA FO                SPECIAL QUALIFICATION                    MO TU WE TH FR SA SU",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "trip_header_1": ParseResult(
        current_state="trip_header",
        parsed_data=TripHeader(
            source=IndexedString(
                idx=1,
                txt="SEQ 25064   1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU",
            ),
            number="25064",
            ops_count="1",
            positions="CA FO",
            operations="",
            special_qualification="",
            calendar="",
        ),
    ),
    "trip_header_2": ParseResult(
        current_state="trip_header",
        parsed_data=TripHeader(
            source=IndexedString(
                idx=2,
                txt="SEQ 6292    1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU",
            ),
            number="6292",
            ops_count="1",
            positions="CA FO",
            operations="SPANISH",
            special_qualification="",
            calendar="",
        ),
    ),
    "trip_header_3": ParseResult(
        current_state="trip_header",
        parsed_data=TripHeader(
            source=IndexedString(
                idx=3,
                txt="SEQ 16945   1 OPS   POSN CA FO                SPECIAL QUALIFICATION                    MO TU WE TH FR SA SU",
            ),
            number="16945",
            ops_count="1",
            positions="CA FO",
            operations="",
            special_qualification="SPECIAL QUALIFICATION",
            calendar="",
        ),
    ),
}


PARSER = line_parser.TripHeader()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "trip_header"
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
