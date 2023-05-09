from importlib import resources
from logging import Logger
from pathlib import Path

from pydantic import parse_raw_as
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.parse_pbs_txt import parse_pbs_txt_file

SERIALIZE_ONLY = False
TEST_DATA = ResourceTestData("three_pages.txt", "02MAY2022_MIA_raw.json")
TEST_FAIL = [ResourceTestData("fail.txt", "")]


def test_page(test_app_data_dir: Path, logger: Logger):
    output_path = test_app_data_dir / "pages" / __name__.rsplit(".", maxsplit=1)[-1]
    debug_path = output_path / f"{TEST_DATA.input_data}_debug.txt"
    res_dir = resources.files(__package__)
    res_file = res_dir.joinpath(TEST_DATA.input_data)

    raw_package, compact_package, expanded_package = parse_pbs_txt_file(
        txt_file=res_file,
        output_dir=output_path,
        debug_path=debug_path,
        compact_out=False,
    )
    assert compact_package is None
    assert expanded_package is None
    if not SERIALIZE_ONLY:
        input_bytes = res_dir.joinpath(TEST_DATA.result_data).read_bytes()
        expected = parse_raw_as(raw.BidPackage, input_bytes)
        assert expected == raw_package
