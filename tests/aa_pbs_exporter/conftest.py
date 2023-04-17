"""conftest.py file for aa_pbs_exporter"""
import json
import logging
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import pytest

# from aa_pbs_exporter.app_lib.logging import rotating_file_handler
from aa_pbs_exporter.snippets.logging.logging import (
    DEFAULT_FORMAT,
    add_handlers_to_target_logger,
    rotating_file_handler,
)
from aa_pbs_exporter.snippets.logging.tz_aware_formatter import TZAwareFormatter

APP_LOG_LEVEL = logging.INFO
TEST_LOG_LEVEL = logging.DEBUG


@dataclass
class PackageResource:
    package: str
    name: str


@dataclass
class FileResource:
    """Stores the file path and file contents."""

    file_path: Path
    data: Any


@pytest.fixture(scope="session", name="logger")
def _logger(test_log_path):
    """A central logger that will log to file."""
    # log_file_name = f"{__name__}.log"
    log_dir: Path = test_log_path
    formatter = TZAwareFormatter(fmt=DEFAULT_FORMAT)
    handler = rotating_file_handler(
        log_dir=log_dir,
        file_name=__name__,
        log_level=TEST_LOG_LEVEL,
        formater=formatter,
    )
    test_logger = logging.getLogger(__name__)
    test_logger.setLevel(TEST_LOG_LEVEL)
    test_logger.addHandler(handler)
    test_logger.warning("Does this even work?")
    test_logger.info(
        "Rotating file logger %s initialized with handler= %r", __name__, handler
    )
    # chunk_logger = logging.getLogger("pfmsoft.text_chunk_parser")
    # chunk_logger.addHandler(handler)
    # chunk_logger.setLevel(TEST_LOG_LEVEL)
    # logger.info("%s library added to log file.", "pfmsoft.text_chunk_parser")
    project_logger = logging.getLogger("aa_pbs_exporter")
    add_handlers_to_target_logger(test_logger, project_logger)
    project_logger.setLevel(TEST_LOG_LEVEL)
    test_logger.info("%s logs added to log file.", "aa_pbs_exporter")
    return test_logger


@pytest.fixture(scope="session", name="test_log_path")
def test_log_path_(test_app_data_dir) -> Path:
    """Make a test-log directory under the app data directory"""
    log_path = test_app_data_dir / Path("test-logs")
    print(f"Logging at: {log_path}")
    return log_path


@pytest.fixture(scope="session", name="test_app_data_dir")
def test_app_data_dir_(tmp_path_factory) -> Path:
    """make a temp directory for app data."""
    test_app_data_dir = tmp_path_factory.mktemp("aa_pbs_exporter")
    return test_app_data_dir


@pytest.fixture(scope="session", name="json_resources")
def json_resources_example_(logger: logging.Logger) -> Dict[str, FileResource]:
    """
    Load all json resource files in a directory to a dict indexed by file name.

    Excludes __init__.py
    """
    json_resources = {}
    resource_path: str = "tests.aa_pbs_exporter.resources.example.json_resources"
    resource_names = collect_resource_names(resource_path, [".json"])
    for name in resource_names:
        resource = load_json_resource(resource_path, name, logger)
        json_resources[name] = resource
    return json_resources


def load_json_resource(
    resource_path: str, resource_name: str, logger: logging.Logger
) -> FileResource:
    resource = load_file_resource(resource_path, resource_name, logger)
    resource.data = json.loads(resource.data)
    return resource


def package_resource_files(resource_package: str) -> Sequence[PackageResource]:
    result = []
    for file in resources.files(resource_package).iterdir():
        if file.is_file() and not file.name.startswith("__"):
            result.append(PackageResource(resource_package, file.name))
    return result


@pytest.fixture(scope="session", name="pairing_text_files")
def pairing_text_file_resources(logger: logging.Logger):
    resource_path: str = "tests.aa_pbs_exporter.resources.text.2022_05"
    # result = []
    # for file in resources.files(resource_path).iterdir():
    #     result.append(PackageResource(resource_path, file.name))

    # resource_names = collect_resource_names(resource_path, [".txt"])
    # file_resources = load_file_resources(
    #     resource_path, resource_names, logger, path_only=True
    # )
    return package_resource_files(resource_path)


# TODO move file resource loading to applib
def load_file_resources(
    resource_path: str,
    resource_names: List[str],
    logger: logging.Logger,
    include_suffixes: Optional[List[str]] = None,
    path_only: bool = False,
    read_text: bool = True,
) -> Dict[str, FileResource]:
    """
    Load all the files found at a resource location.

    [extended_summary]

    Args:
        resource_path: package path to resource folder, eg. tests.resources.photos
        resource_names: A list of resources to load. An empty list means load all files found.
        logger: logger, usually passed in from a pytest.fixture
        exclude_suffixes: A list of string suffixes to exclude. eg. [".txt",".png"]. Defaults to None.
        path_only: Do not read the file. Defaults to False.
        read_text: Read file as text. Defaults to True.

    Returns:
        A dict of file resources
    """
    if not resource_names:
        file_names = collect_resource_names(resource_path, include_suffixes)
    else:
        file_names = resource_names
    file_resources = {}
    for file_name in file_names:
        file_resource = load_file_resource(
            resource_path, file_name, logger, path_only, read_text
        )
        file_resources[file_name] = file_resource
    return file_resources


def load_file_resource(
    resource_path: str,
    resource_name: str,
    logger: logging.Logger,
    path_only: bool = False,
    read_text: bool = True,
) -> FileResource:
    """
    Load a file resource.

    Load a string or bytes as a FileResource. Can optionaly return only a path to a
    file, with None as data.

    Args:
        resource_path: package path to resource folder, eg. tests.resources.photos
        resource_name: file name of resource, eg. beach.jpeg
        logger: logger, usually passed in from a pytest.fixture
        path_only: Do not read the file. Defaults to False.
        read_text: Read file as text. Defaults to True.

    Raises:
        ex: [description]

    Returns:
        FileResource: [description]
    """
    try:
        with resources.path(resource_path, resource_name) as data_path:
            data: Optional[Union[str, bytes]] = None
            if read_text:
                if not path_only:
                    data = data_path.read_text()
                    logger.debug(
                        "Loaded resource file %s from %s", resource_name, resource_path
                    )
                return FileResource(file_path=data_path, data=data)
            else:
                if not path_only:
                    data = data_path.read_bytes()
                    logger.debug(
                        "Loaded resource file %s from %s", resource_name, resource_path
                    )
                return FileResource(file_path=data_path, data=data)
    # TODO refine the exception handling for files, and resource loading.
    except Exception as ex:
        logger.exception(
            "Unable to load resource file %s from %s Error msg %s",
            resource_name,
            resource_path,
            ex,
        )
        raise ex


def collect_resource_names(
    resource_path: str,
    include_suffixes: Optional[List[str]] = None,
) -> List[str]:
    """
    Returns a list of file names in a resource directory, excluding the __init__.py

    [extended_summary]

    Args:
        resource_path: package path to resource folder, eg. tests.resources.photos
        include_suffixes: A list of string suffixes to include. eg. [".txt",".png"]. Defaults to None.

    Returns:
        A list of file names in a resource directory.
    """

    if include_suffixes is None:
        include_suffixes = []
    result = []
    with resources.path(resource_path, "__init__.py") as data_path:
        for file in (x for x in data_path.parent.glob("*.*") if x.is_file()):
            if file.name != "__init__.py":
                if not include_suffixes or file.suffix in include_suffixes:
                    result.append(file.name)
    return result


# def make_file_resource(resource_path, resource_name, logger) -> FileResource:
#     try:
#         with resources.path(resource_path, resource_name) as data_path:
#             data = data_path.read_text()
#             logger.debug(
#                 "Loaded resource file %s from %s", resource_name, resource_path
#             )
#             return FileResource(file_path=data_path, data=data)
#     except Exception as ex:
#         logger.exception(
#             "Unable to load resource file %s from %s Error msg %s",
#             resource_name,
#             resource_path,
#             ex,
#         )
#         raise ex


@pytest.fixture(autouse=True)
def env_setup(monkeypatch, test_app_data_dir):
    """environment variables set for each test."""
    monkeypatch.setenv(
        "PFMSOFT_AA_PBS_EXPORTER_TESTING",
        "True",
    )
    monkeypatch.setenv(
        "PFMSOFT_AA_PBS_EXPORTER_LOG_LEVEL",
        str(APP_LOG_LEVEL),
    )
    monkeypatch.setenv(
        "PFMSOFT_AA_PBS_EXPORTER_APP_DIR",
        str(test_app_data_dir),
    )
