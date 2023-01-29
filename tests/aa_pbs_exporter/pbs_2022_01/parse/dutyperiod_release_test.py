from pathlib import Path

from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    raw.DutyPeriodRelease(
        source=IndexedString(
            1,
            "                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−",
        ),
        release="0739/0439",
        block="4.49",
        synth="0.00",
        total_pay="4.49",
        duty="6.19",
        flight_duty="5.49",
        calendar="−− −− −− −− −− −− −−",
    ),
    raw.DutyPeriodRelease(
        source=IndexedString(
            1,
            "                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00",
        ),
        release="2252/2252",
        block="0.00",
        synth="5.46",
        total_pay="5.46",
        duty="6.46",
        flight_duty="0.00",
        calendar="",
    ),
]


def test_dutyperiod_release(test_app_data_dir: Path):
    run_line_test(
        name="test_dutyperiod_release",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="dutyperiod_release",
        parser=line_parser.DutyPeriodRelease(),
    )
