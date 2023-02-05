from pathlib import Path

from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    raw.PageFooter(
        source=raw.IndexedString(
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
    raw.PageFooter(
        source=raw.IndexedString(
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
]


def test_page_footer(test_app_data_dir: Path):
    run_line_test(
        name="test_page_footer",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="page_footer",
        parser=line_parser.PageFooter(),
    )
