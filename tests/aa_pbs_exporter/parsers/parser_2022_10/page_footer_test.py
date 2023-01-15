from pathlib import Path

from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.parsing.indexed_string import IndexedString
from aa_pbs_exporter.util.parsing.parse_context import DevParseContext

test_data = [
    lines.PageFooter(
        source=IndexedString(
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
        source=IndexedString(
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


def test_page_footer(test_app_data_dir: Path):
    run_line_test(
        name="test_page_footer",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="page_footer",
        parser=line_parser.PageFooter(),
    )
