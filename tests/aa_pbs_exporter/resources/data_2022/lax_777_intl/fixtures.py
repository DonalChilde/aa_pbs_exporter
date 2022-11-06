from tests.aa_pbs_exporter.resources.helpers import (
    ParseTestingData,
    build_testing_data,
    parent_package_path,
)
import pytest


@pytest.fixture(scope="module", name="lax_777_intl")
def _lax_777_intl() -> ParseTestingData:
    ptd = build_testing_data(parent_package_path(__name__), "data")
    return ptd
