from importlib import resources
from logging import Logger
from pathlib import Path

from pydantic import parse_raw_as
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData

from aa_pbs_exporter.pbs_2022_01 import translate
from aa_pbs_exporter.pbs_2022_01.helpers.init_msg_bus import init_msg_bus
from aa_pbs_exporter.pbs_2022_01.helpers.init_parse_manager import init_parse_manager
from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_file import parse_pbs_file
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded, raw
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out

SERIALIZE_ONLY = False
RAW_TEST_DATA = ResourceTestData("one_page.txt", "one_page_raw.json")
COMPACT_TEST_DATA = ResourceTestData(RAW_TEST_DATA.result_data, "one_page_compact.json")
EXPANDED_TEST_DATA = ResourceTestData(
    COMPACT_TEST_DATA.result_data, "one_page_expanded.json"
)
TEST_FAIL = [ResourceTestData("fail.txt", "")]


def test_page(test_app_data_dir: Path, logger: Logger):
    output_path = (
        test_app_data_dir
        / "translate"
        / "to_expanded"
        / __name__.rsplit(".", maxsplit=1)[-1]
    )
    output_path.mkdir(parents=True, exist_ok=True)
    debug_path = output_path / f"{RAW_TEST_DATA.input_data}_debug.txt"
    res_dir = resources.files(__package__)
    res_file = res_dir.joinpath(RAW_TEST_DATA.input_data)

    with open(debug_path, "w", encoding="utf-8") as debug_fp:
        msg_bus = init_msg_bus(debug_fp=debug_fp, click_out=False)
        manager = init_parse_manager(source_path=res_file, msg_bus=msg_bus)
        raw_bid_package = parse_pbs_file(file_path=res_file, manager=manager)
        compact_package = translate.raw_to_compact(
            raw_package=raw_bid_package, msg_bus=msg_bus
        )
        expanded_package = translate.compact_to_expanded(
            compact_package=compact_package, msg_bus=msg_bus
        )

    bid_package_path = output_path / RAW_TEST_DATA.result_data
    bid_package_path.write_text(raw_bid_package.json(indent=2))

    compact_json_path = output_path / COMPACT_TEST_DATA.result_data
    validate_file_out(compact_json_path)
    compact_json_path.write_text(compact_package.json(indent=2))

    expanded_json_path = output_path / EXPANDED_TEST_DATA.result_data
    validate_file_out(expanded_json_path)
    expanded_json_path.write_text(expanded_package.json(indent=2))

    if not SERIALIZE_ONLY:
        input_bytes = res_dir.joinpath(RAW_TEST_DATA.result_data).read_bytes()
        raw_expected = parse_raw_as(raw.BidPackage, input_bytes)
        assert raw_expected == raw_bid_package
        input_bytes = res_dir.joinpath(COMPACT_TEST_DATA.result_data).read_bytes()
        compact_expected = parse_raw_as(compact.BidPackage, input_bytes)
        assert compact_expected == compact_package
        input_bytes = res_dir.joinpath(EXPANDED_TEST_DATA.result_data).read_bytes()
        expanded_expected = parse_raw_as(expanded.BidPackage, input_bytes)
        assert expanded_expected == expanded_package
    # assert False
