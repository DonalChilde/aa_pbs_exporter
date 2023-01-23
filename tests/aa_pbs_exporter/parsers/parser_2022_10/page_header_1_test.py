from pathlib import Path

from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    lines.PageHeader1(
        source=IndexedString(
            1,
            "   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/",
        )
    ),
]


def test_page_header_1(test_app_data_dir: Path):
    run_line_test(
        name="test_page_header_1",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="page_header_1",
        parser=line_parser.PageHeader1(),
    )
