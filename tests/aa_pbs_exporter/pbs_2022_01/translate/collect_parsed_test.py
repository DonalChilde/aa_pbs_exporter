from importlib import resources
from logging import Logger
from pathlib import Path

import pytest

from aa_pbs_exporter.pbs_2022_01.helpers.serialize_json import SerializeJson
from aa_pbs_exporter.pbs_2022_01.models.collated import BidPackage
from aa_pbs_exporter.pbs_2022_01.translate.collate_parse_results import (
    collate_parse_results,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
)
from tests.aa_pbs_exporter.resources import RESOURCE_PATH
from tests.aa_pbs_exporter.resources.helpers_3 import ResourceLocator


def worker_collect(
    test_app_data_dir: Path, logger: Logger, file_stem: str, page_count: int
):
    _ = logger
    input_res = ResourceLocator(f"{RESOURCE_PATH}.parsed", f"{file_stem}-parsed.json")
    output_path = test_app_data_dir / "collect_parsed" / f"{file_stem}-collected.json"
    expected_res = ResourceLocator(
        f"{RESOURCE_PATH}.collected", f"{file_stem}-collected.json"
    )
    input_serializer = SerializeJson[CollectedParseResults]("CollectedParseResults")
    expected_serializer = SerializeJson[BidPackage]("collected.BidPackage")
    output_serializer = SerializeJson[BidPackage]("BidPackage")
    with resources.as_file(input_res.file_resource()) as input_path:
        parse_results = input_serializer.load_json(input_path)
    bid_package = collate_parse_results(parse_results=parse_results)
    output_serializer.save_json(output_path, bid_package)
    with resources.as_file(expected_res.file_resource()) as expected_path:
        expected = expected_serializer.load_json(expected_path)
    assert expected == bid_package
    assert len(bid_package["pages"]) == page_count


def test_collect_one_page(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "one_page"
    page_count = 1

    worker_collect(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


def test_collect_three_pages(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "three_pages"
    page_count = 3

    worker_collect(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


def test_collect_small_package(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "PBS_DCA_May_2022_20220408124308"
    page_count = 173

    worker_collect(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )


@pytest.mark.slow
def test_collect_large_package(test_app_data_dir: Path, logger: Logger):
    file_stem: str = "PBS_DFW_May_2022_20220408124407"
    page_count = 920

    worker_collect(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        page_count=page_count,
    )
