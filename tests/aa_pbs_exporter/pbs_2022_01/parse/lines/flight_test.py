from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_lines

from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.pbs_2022_01.models.raw import Flight, IndexedString
from aa_pbs_exporter.pbs_2022_01.parse import ParseResultProtocol
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

test_data = [
    ParseTestData(
        name="flight_1",
        txt="1  1/1 65 2131  SAN 1337/1337    ORD 1935/1735   3.58          1.10X                   −− −− −− −− −− −− −−",
        description="Flight with ground time and equipment change",
    ),
]

result_data = {
    "flight_1": ParseResultProtocol(
        current_state="flight",
        parsed_data=Flight(
            source=IndexedString(
                idx=1,
                txt="1  1/1 65 2131  SAN 1337/1337    ORD 1935/1735   3.58          1.10X                   −− −− −− −− −− −− −−",
            ),
            dutyperiod_idx="1",
            dep_arr_day="1/1",
            eq_code="65",
            flight_number="2131",
            deadhead="",
            departure_station="SAN",
            departure_time="1337/1337",
            meal="",
            arrival_station="ORD",
            arrival_time="1935/1735",
            block="3.58",
            synth="0.00",
            ground="1.10",
            equipment_change="X",
            calendar="−− −− −− −− −− −− −−",
        ),
    )
}


PARSER = line_parser.Flight()


def test_all(test_app_data_dir: Path):
    outpath = test_app_data_dir / "lines" / "flight"
    parse_lines(
        test_data=test_data,
        result_data=result_data,
        parser=PARSER,
        output_path=outpath,
        # skip_test=True,
    )


def test_parse_fail():
    with pytest.raises(ParseException):
        PARSER.parse(IndexedString(idx=1, txt="foo"), ctx={})
