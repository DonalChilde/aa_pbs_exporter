from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser

test_data = [
    lines.Transportation(
        source=lines.SourceText(
            1,
            "                    SIN FIN DE SERVICIOS                    3331223240",
        ),
        name="SIN FIN DE SERVICIOS",
        phone="3331223240",
        calendar="",
    ),
    lines.Transportation(
        source=lines.SourceText(
            2,
            "                    VIP TRANSPORTATION− OGG                 8088712702                 −− −− −−",
        ),
        name="VIP TRANSPORTATION− OGG",
        phone="8088712702",
        calendar="−− −− −−",
    ),
    lines.Transportation(
        source=lines.SourceText(
            2,
            "                                                                                      −− −− −−",
        ),
        name="",
        phone="",
        calendar="−− −− −−",
    ),
]

#                                                                                       −− −− −−
def test_transportation(logger):
    ctx = ParseContextTest("None")
    expected_state = "transportation"
    parser = line_parser.Transportation()
    for data in test_data:
        state = parser.parse(data.source.line_no, data.source.txt, ctx)
        assert state == expected_state
        assert data == ctx.parsed_data
