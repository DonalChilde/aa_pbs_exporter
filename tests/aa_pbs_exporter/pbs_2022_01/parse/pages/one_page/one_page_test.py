from importlib import resources
from logging import Logger
from pathlib import Path

from pydantic import parse_raw_as
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData

from aa_pbs_exporter.pbs_2022_01.helpers import debug_parse_raw_bidpackage
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.parse_manager import ParseManager

SERIALIZE_ONLY = False
TEST_DATA = ResourceTestData("one_page.txt", "one_page.json")
TEST_FAIL = [ResourceTestData("fail.txt", "")]


def test_page(test_app_data_dir: Path, logger: Logger):
    output_path = test_app_data_dir / "pages" / __name__.rsplit(".", maxsplit=1)[-1]
    manager = ParseManager(ctx={})
    debug_path = output_path / f"{TEST_DATA.input_data}_debug.txt"
    res_dir = resources.files(__package__)
    res_file = res_dir.joinpath(TEST_DATA.input_data)
    bid_package = debug_parse_raw_bidpackage(
        source_path=res_file,
        manager=manager,
        debug_file_path=debug_path,
    )
    bid_package_path = output_path / TEST_DATA.result_data
    bid_package_path.write_text(bid_package.json(indent=2))
    if not SERIALIZE_ONLY:
        input_bytes = res_dir.joinpath(TEST_DATA.result_data).read_bytes()
        expected = parse_raw_as(raw.BidPackage, input_bytes)
        assert expected == bid_package
