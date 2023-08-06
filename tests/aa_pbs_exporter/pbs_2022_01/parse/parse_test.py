from importlib import resources
from logging import Logger
from pathlib import Path

import pytest

from aa_pbs_exporter.pbs_2022_01 import api
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseException,
)
from tests.aa_pbs_exporter.resources import RESOURCE_PATH
from tests.aa_pbs_exporter.resources.helpers_3 import (
    ResourceLocator,
    hashed_file_from_resource,
)

SERIALIZE_ONLY = False


def worker_parse(
    test_app_data_dir: Path,
    logger: Logger,
    file_stem: str,
    job_name: str,
):
    _ = logger
    output_dir = test_app_data_dir / "parsed"
    json_path = output_dir / f"{file_stem}-parsed.json"
    debug_path = output_dir / f"{file_stem}.parsed-debug.txt"
    input_resource = ResourceLocator(
        f"{RESOURCE_PATH}.extracted_txt", f"{file_stem}.txt"
    )
    expected_resource = ResourceLocator(
        f"{RESOURCE_PATH}.parsed", f"{file_stem}-parsed.json"
    )
    hashed_file = hashed_file_from_resource(input_resource)
    with resources.as_file(input_resource.file_resource()) as file_in:
        result = api.parse_pbs_txt_file(
            file_in=file_in,
            debug_file=debug_path,
            job_name=job_name,
            metadata={"source": hashed_file},
        )
        api.save_parse_results(file_out=json_path, parse_results=result)
    if not SERIALIZE_ONLY:
        with resources.as_file(expected_resource.file_resource()) as expected_file:
            expected = api.load_parse_results(file_in=expected_file)
        assert result == expected


def test_one_page(test_app_data_dir: Path, logger: Logger):
    file_stem = "one_page"
    job_name = "One Page"

    worker_parse(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        job_name=job_name,
    )


def test_three_pages(test_app_data_dir: Path, logger: Logger):
    file_stem = "three_pages"
    job_name = "Three Pages"

    worker_parse(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        job_name=job_name,
    )


def test_transportation_no_phone(test_app_data_dir: Path, logger: Logger):
    file_stem = "transportation_no_phone"
    job_name = "transportation_no_phone"

    worker_parse(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        job_name=job_name,
    )


@pytest.mark.slow
def test_small_package(test_app_data_dir: Path, logger: Logger):
    file_stem = "PBS_DCA_May_2022_20220408124308"
    job_name = "PBS_DCA_May_2022"

    worker_parse(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        job_name=job_name,
    )


@pytest.mark.slow
def test_large_package(test_app_data_dir: Path, logger: Logger):
    file_stem = "PBS_DFW_May_2022_20220408124407"
    job_name = "PBS_DFW_May_2022"

    worker_parse(
        test_app_data_dir=test_app_data_dir,
        logger=logger,
        file_stem=file_stem,
        job_name=job_name,
    )


# TODO more parse fail conditions, eg. no text. no parse start trigger, incomplete parse - text left over
def test_fail(test_app_data_dir: Path, logger: Logger):
    _ = logger
    file_stem = "fail"
    job_name = "Parse Fail"

    output_path = test_app_data_dir / "parsed"
    json_path = output_path / f"{file_stem}-parsed.json"
    debug_path = output_path / f"{file_stem}.parsed-debug.txt"

    input_resource = ResourceLocator(
        f"{RESOURCE_PATH}.extracted_txt", f"{file_stem}.txt"
    )

    hashed_file = hashed_file_from_resource(input_resource)
    with resources.as_file(input_resource.file_resource()) as file_in:
        with pytest.raises(ParseException):
            result = api.parse_pbs_txt_file(
                file_in=file_in,
                debug_file=debug_path,
                job_name=job_name,
                metadata={"source": hashed_file},
            )
            api.save_parse_results(file_out=json_path, parse_results=result)
