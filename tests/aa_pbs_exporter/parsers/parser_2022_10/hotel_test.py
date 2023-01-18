from pathlib import Path

from tests.aa_pbs_exporter.parsers.parser_2022_10.test_context import ParseContextTest
from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext

test_data = [
    lines.Hotel(
        source=IndexedString(
            1,
            "                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
        ),
        layover_city="MIA",
        name="SONESTA MIAMI AIRPORT",
        phone="13054469000",
        rest="11.27",
        calendar="−− −− −− −− −− −− −−",
    ),
    lines.Hotel(
        source=IndexedString(
            2,
            "                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
        ),
        layover_city="LHR",
        name="PARK PLAZA WESTMINSTER BRIDGE LONDON",
        phone="443334006112",
        rest="24.00",
        calendar="−− −− −− −− −− −− −−",
    ),
]


def test_hotel(test_app_data_dir: Path):
    run_line_test(
        name="test_hotel",
        output_dir=test_app_data_dir,
        test_data=test_data,
        expected_state="hotel",
        parser=line_parser.Hotel(),
    )
