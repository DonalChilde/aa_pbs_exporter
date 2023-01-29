from pathlib import Path

from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    raw.HeaderSeparator(
        source=IndexedString(
            1,
            "−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−",
        ),
    ),
]


def test_header_separator(test_app_data_dir: Path):
    run_line_test(
        name="test_header_separator",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="header_separator",
        parser=line_parser.HeaderSeparator(),
    )
