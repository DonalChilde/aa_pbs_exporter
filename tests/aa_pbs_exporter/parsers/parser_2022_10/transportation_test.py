from pathlib import Path

from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString

test_data = [
    lines.Transportation(
        source=IndexedString(
            1,
            "                    SIN FIN DE SERVICIOS                    3331223240",
        ),
        name="SIN FIN DE SERVICIOS",
        phone="3331223240",
        calendar="",
    ),
    lines.Transportation(
        source=IndexedString(
            2,
            "                    VIP TRANSPORTATION− OGG                 8088712702                 −− −− −−",
        ),
        name="VIP TRANSPORTATION− OGG",
        phone="8088712702",
        calendar="−− −− −−",
    ),
    lines.Transportation(
        source=IndexedString(
            2,
            "                                                                                      −− −− −−",
        ),
        name="",
        phone="",
        calendar="−− −− −−",
    ),
]

#                                                                                       −− −− −−
def test_transportation(test_app_data_dir: Path):
    run_line_test(
        name="test_transportation",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="transportation",
        parser=line_parser.Transportation(),
    )
