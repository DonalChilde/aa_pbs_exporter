import pytest
from tests.aa_pbs_exporter.resources.helpers import (
    ParseTestingData,
    build_testing_data,
    parent_package_path,
)


@pytest.fixture(scope="module", name="lax_777_intl")
def lax_777_intl_fixture() -> ParseTestingData:
    ptd = build_testing_data(parent_package_path(__name__), "data", "lax_777_intl")
    return ptd
