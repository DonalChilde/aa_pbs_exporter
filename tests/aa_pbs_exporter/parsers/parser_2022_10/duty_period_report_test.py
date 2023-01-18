from pathlib import Path
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext
from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from tests.aa_pbs_exporter.resources.helpers import run_line_test

test_data = [
    lines.DutyPeriodReport(
        source=IndexedString(
            1,
            "                RPT 1237/1237                                                           2 −− −− −− −− −− −−",
        ),
        report="1237/1237",
        calendar="2 −− −− −− −− −− −−",
    ),
]


def test_dutyperiod_report(test_app_data_dir: Path):
    run_line_test(
        name="test_dutyperiod_report",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="dutyperiod_report",
        parser=line_parser.DutyPeriodReport(),
    )
