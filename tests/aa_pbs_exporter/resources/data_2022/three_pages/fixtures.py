import pytest
from tests.aa_pbs_exporter.resources.helpers import (
    ParseTestingData,
    build_testing_data,
    parent_package_path,
)


@pytest.fixture(scope="module", name="three_pages")
def three_pages_fixture() -> ParseTestingData:
    ptd = build_testing_data(parent_package_path(__name__), "data", "three_pages")
    return ptd
