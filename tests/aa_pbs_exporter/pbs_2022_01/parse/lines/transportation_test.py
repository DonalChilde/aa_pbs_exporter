from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parsers as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import IndexedString, Transportation
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="transportation_1",
        txt="                    SIN FIN DE SERVICIOS                    3331223240",
        description="A base equipment with no satellite base",
    ),
    ParseTestData(
        name="transportation_2",
        txt="                    VIP TRANSPORTATION− OGG                 8088712702                 −− −− −−",
        description="A base equipment with satellite base",
    ),
    ParseTestData(
        name="transportation_3",
        txt="                                                                                      −− −− −−",
        description="A base equipment with satellite base",
    ),
]

result_data = {
    "transportation_1": ParseResult(
        current_state="transportation",
        parsed_data=Transportation(
            source=IndexedString(
                idx=1,
                txt="                    SIN FIN DE SERVICIOS                    3331223240",
            ),
            name="SIN FIN DE SERVICIOS",
            phone="3331223240",
            calendar="",
        ),
    ),
    "transportation_2": ParseResult(
        current_state="transportation",
        parsed_data=Transportation(
            source=IndexedString(
                idx=2,
                txt="                    VIP TRANSPORTATION− OGG                 8088712702                 −− −− −−",
            ),
            name="VIP TRANSPORTATION− OGG",
            phone="8088712702",
            calendar="−− −− −−",
        ),
    ),
    "transportation_3": ParseResult(
        current_state="transportation",
        parsed_data=Transportation(
            source=IndexedString(
                idx=3,
                txt="                                                                                      −− −− −−",
            ),
            name="",
            phone="",
            calendar="−− −− −−",
        ),
    ),
}


PARSER = line_parser.Transportation()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "transportation"
    parse_lines(
        test_data=test_data,
        result_data=result_data,
        parser=PARSER,
        output_path=outpath,
        # skip_test=True,
    )


# FIXME this parser succeeds on anything?
# def test_parse_fail():
#     with pytest.raises(ParseException):
#         PARSER.parse(IndexedString(idx=1, txt=""), ctx={})
