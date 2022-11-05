from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser

test_data = [
    lines.PageFooter(
        source=lines.SourceText(
            1,
            "COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 737  DOM                              PAGE   644",
        ),
        issued="08APR2022",
        effective="02MAY2022",
        base="LAX",
        satelite_base="",
        equipment="737",
        division="DOM",
        page="644",
    ),
    lines.PageFooter(
        source=lines.SourceText(
            2,
            "COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 320  INTL                             PAGE  1178",
        ),
        issued="08APR2022",
        effective="02MAY2022",
        base="LAX",
        satelite_base="",
        equipment="320",
        division="INTL",
        page="1178",
    ),
]


def test_page_footer():
    ctx = ParseContextTest("None")
    expected_state = "page_footer"
    parser = line_parser.PageFooter()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        print("expected", ctx.parsed_data)
        print("parsed", ctx.parsed_data)
        assert data == ctx.parsed_data
