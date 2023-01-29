from pathlib import Path

from tests.aa_pbs_exporter.pbs_2022_01.parse.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString

test_data = [
    raw.Transportation(
        source=IndexedString(
            1,
            "                    SIN FIN DE SERVICIOS                    3331223240",
        ),
        name="SIN FIN DE SERVICIOS",
        phone="3331223240",
        calendar="",
    ),
    raw.Transportation(
        source=IndexedString(
            2,
            "                    VIP TRANSPORTATION− OGG                 8088712702                 −− −− −−",
        ),
        name="VIP TRANSPORTATION− OGG",
        phone="8088712702",
        calendar="−− −− −−",
    ),
    raw.Transportation(
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
