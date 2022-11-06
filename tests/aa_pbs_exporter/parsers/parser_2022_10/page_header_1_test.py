from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.indexed_string import IndexedString

test_data = [
    lines.PageHeader1(
        source=IndexedString(
            1,
            "   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/",
        )
    ),
]


def test_page_header_1():
    ctx = ParseContextTest("None")
    expected_state = "page_header_1"
    parser = line_parser.PageHeader1()
    for data in test_data:
        state = parser.parse(data.source, ctx)
        assert state == expected_state
        assert data == ctx.parsed_data
