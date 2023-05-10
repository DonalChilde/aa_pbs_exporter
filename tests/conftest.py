"""conftest.py file for aa_pbs_exporter"""
import logging
from pathlib import Path

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item

from aa_pbs_exporter.snippets.logging.logging import (
    add_handlers_to_target_logger,
    rotating_file_handler,
)

APP_LOG_LEVEL = logging.INFO
TEST_LOG_LEVEL = logging.DEBUG


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def pytest_addoption(parser: Parser):
    # https://docs.pytest.org/en/stable/example/simple.html#control-skipping-of-tests-according-to-command-line-option
    # conftest.py must be in the root test package.
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config: Config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config: Config, items: list[Item]):
    if config.getoption("--run-slow"):
        # --run-slow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope="session", name="logger")
def _logger(test_log_path):
    """A central logger that will log to file."""
    log_dir: Path = test_log_path
    handler = rotating_file_handler(
        log_dir=log_dir,
        file_name=__name__,
        log_level=TEST_LOG_LEVEL,
    )
    test_logger = logging.getLogger(__name__)
    test_logger.setLevel(TEST_LOG_LEVEL)
    test_logger.addHandler(handler)
    test_logger.warning("Does this even work?")
    test_logger.info(
        "Rotating file logger %s initialized with handler= %r", __name__, handler
    )
    project_logger = logging.getLogger("aa_pbs_exporter")
    add_handlers_to_target_logger(test_logger, project_logger)
    project_logger.setLevel(APP_LOG_LEVEL)
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
