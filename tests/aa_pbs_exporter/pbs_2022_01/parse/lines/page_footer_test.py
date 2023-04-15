from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parsers as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import IndexedString, PageFooter
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="page_footer_1",
        txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 737  DOM                              PAGE   644",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="page_footer_2",
        txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 320  INTL                             PAGE  1178",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "page_footer_1": ParseResult(
        current_state="page_footer",
        parsed_data=PageFooter(
            source=IndexedString(
                idx=1,
                txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 737  DOM                              PAGE   644",
            ),
            issued="08APR2022",
            effective="02MAY2022",
            base="LAX",
            satelite_base="",
            equipment="737",
            division="DOM",
            page="644",
        ),
    ),
    "page_footer_2": ParseResult(
        current_state="page_footer",
        parsed_data=PageFooter(
            source=IndexedString(
                idx=2,
                txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 320  INTL                             PAGE  1178",
            ),
            issued="08APR2022",
            effective="02MAY2022",
            base="LAX",
            satelite_base="",
            equipment="320",
            division="INTL",
            page="1178",
        ),
    ),
}


PARSER = line_parser.PageFooter()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "page_footer"
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
