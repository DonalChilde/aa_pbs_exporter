from pathlib import Path
from aa_pbs_exporter.util.parsing.parse_context import DevParseContext
from aa_pbs_exporter.util.parsing.state_parser import Parser
from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.parsing.indexed_string import IndexedString
from tests.aa_pbs_exporter.resources.helpers import run_line_test

test_data = [
    lines.PageHeader2(
        source=IndexedString(
            1,
            "DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01",
        ),
        calendar_range="05/02−06/01",
    ),
]


def test_page_header_2(test_app_data_dir: Path):
    run_line_test(
        name="test_page_header_2_2",
        output_dir=test_app_data_dir,
        expected_state="page_header_2",
        parser=line_parser.PageHeader2(),
        test_data=test_data,
    )
