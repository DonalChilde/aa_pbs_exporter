from importlib import resources
from logging import Logger
import pytest
from pathlib import Path

from tests.aa_pbs_exporter.resources import RESOURCE_PATH
from tests.aa_pbs_exporter.resources.helpers_3 import ResourceLocator
from aa_pbs_exporter.pbs_2022_01 import api

SERIALIZE_ONLY = False


def worker_expand(
    test_app_data_dir: Path, logger: Logger, file_stem: str, page_count: int
):
    _ = logger
    input_res = ResourceLocator(f"{RESOURCE_PATH}.compact", f"{file_stem}-compact.json")
    output_dir = test_app_data_dir / "expanded"
    output_file = output_dir / f"{file_stem}-expanded.json"
    debug_file = output_dir / f"{file_stem}-expanded-debug.txt"
    expected_res = ResourceLocator(
        f"{RESOURCE_PATH}.expanded", f"{file_stem}-expanded.json"
    )

    with resources.as_file(input_res.file_resource()) as input_path:
        compact_bid_package = api.load_compact(file_in=input_path)
    (
        expanded_bid_package,
        translation_errors,
        validation_errors,
    ) = api.compact_to_expanded(bid_package=compact_bid_package, debug_file=debug_file)
    api.save_expanded(file_out=output_file, bid_package=expanded_bid_package)
    print(f"translation errors: {translation_errors!s}")
    print(f"validation errors: {validation_errors!s}")
    assert not translation_errors
    assert not validation_errors
    if not SERIALIZE_ONLY:
        with resources.as_file(expected_res.file_resource()) as expected_path:
            expected = api.load_expanded(file_in=expected_path)
        assert expected == expanded_bid_package
        assert len(expanded_bid_package.pages) == page_count


def test_expand_one_page(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "one_page"
    page_count = 1

    worker_expand(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


def test_expand_three_pages(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "three_pages"
    page_count = 3

    worker_expand(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


def test_expand_transportation_no_phone(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "transportation_no_phone"
    page_count = 2

    worker_expand(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


@pytest.mark.slow
def test_expand_small_package(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "PBS_DCA_May_2022_20220408124308"
    page_count = 173

    worker_expand(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


@pytest.mark.slow
def test_expand_large_package(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "PBS_DFW_May_2022_20220408124407"
    page_count = 920

    worker_expand(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )
