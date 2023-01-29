from pathlib import Path

from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString

test_data = [
    raw.PageHeader2(
        source=raw.IndexedString(
            idx=1,
            txt="DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01",
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
