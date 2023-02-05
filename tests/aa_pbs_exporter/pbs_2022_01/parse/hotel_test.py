from pathlib import Path

from tests.aa_pbs_exporter.resources.helpers import run_line_test

from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.pbs_2022_01.models import raw

test_data = [
    raw.Hotel(
        source=raw.IndexedString(
            idx=1,
            txt="                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−",
        ),
        layover_city="MIA",
        name="SONESTA MIAMI AIRPORT",
        phone="13054469000",
        rest="11.27",
        calendar="−− −− −− −− −− −− −−",
    ),
    raw.Hotel(
        source=raw.IndexedString(
            idx=2,
            txt="                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−",
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
