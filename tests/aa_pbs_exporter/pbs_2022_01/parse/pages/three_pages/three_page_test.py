from importlib import resources
from logging import Logger
from pathlib import Path

from pydantic import parse_raw_as
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData

from aa_pbs_exporter.pbs_2022_01.helpers.init_msg_bus import init_msg_bus
from aa_pbs_exporter.pbs_2022_01.helpers.init_parse_manager import init_parse_manager
from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_file import parse_pbs_file
from aa_pbs_exporter.pbs_2022_01.models import raw

SERIALIZE_ONLY = False
TEST_DATA = ResourceTestData("three_pages.txt", "three_pages.json")
TEST_FAIL = [ResourceTestData("fail.txt", "")]


def test_page(test_app_data_dir: Path, logger: Logger):
    output_path = test_app_data_dir / "pages" / __name__.rsplit(".", maxsplit=1)[-1]
    output_path.mkdir(parents=True)
    debug_path = output_path / f"{TEST_DATA.input_data}_debug.txt"
    res_dir = resources.files(__package__)
    res_file = res_dir.joinpath(TEST_DATA.input_data)

    with open(debug_path, "w", encoding="utf-8") as debug_fp:
        msg_bus = init_msg_bus(debug_fp=debug_fp, click_out=False)
        manager = init_parse_manager(source_path=res_file, msg_bus=msg_bus)
        bid_package = parse_pbs_file(file_path=res_file, manager=manager)

    bid_package_path = output_path / TEST_DATA.result_data
    bid_package_path.write_text(bid_package.json(indent=2))
    if not SERIALIZE_ONLY:
        input_bytes = res_dir.joinpath(TEST_DATA.result_data).read_bytes()
        expected = parse_raw_as(raw.BidPackage, input_bytes)
        assert expected == bid_package
