from importlib import resources
from logging import Logger
from pathlib import Path

from tests.aa_pbs_exporter.resources import RESOURCE_PATH
from tests.aa_pbs_exporter.resources.helpers_3 import ResourceLocator
from aa_pbs_exporter.pbs_2022_01 import api

SERIALIZE_ONLY = False


def worker_compact(
    test_app_data_dir: Path, logger: Logger, file_stem: str, page_count: int
):
    _ = logger
    input_res = ResourceLocator(
        f"{RESOURCE_PATH}.collected", f"{file_stem}-collected.json"
    )
    output_dir = test_app_data_dir / "compact"
    output_file = output_dir / f"{file_stem}-compact.json"
    debug_file = output_dir / f"{file_stem}-compact-debug.txt"
    expected_res = ResourceLocator(
        f"{RESOURCE_PATH}.compact", f"{file_stem}-compact.json"
    )

    with resources.as_file(input_res.file_resource()) as input_path:
        collated_parse_results = api.load_collated(file_in=input_path)
    compact_bid_package = api.collated_to_compact(
        bid_package=collated_parse_results, debug_file=debug_file
    )
    api.save_compact(file_out=output_file, bid_package=compact_bid_package)

    if not SERIALIZE_ONLY:
        with resources.as_file(expected_res.file_resource()) as expected_path:
            expected = api.load_compact(file_in=expected_path)
        assert expected == compact_bid_package
        assert len(compact_bid_package.pages) == page_count


def test_compact_one_page(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "one_page"
    page_count = 1

    worker_compact(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


def test_compact_three_pages(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "three_pages"
    page_count = 1

    worker_compact(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


def test_compact_small_package(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "PBS_DCA_May_2022_20220408124308"
    page_count = 1

    worker_compact(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


def test_compact_large_package(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "PBS_DFW_May_2022_20220408124407"
    page_count = 1

    worker_compact(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )
