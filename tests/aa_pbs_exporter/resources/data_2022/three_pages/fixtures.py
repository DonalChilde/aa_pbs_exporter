from tests.aa_pbs_exporter.resources.helpers import ParseTestingData, build_testing_data
import pytest


@pytest.fixture(scope="module")
def three_pages() -> ParseTestingData:
    ptd = build_testing_data(__name__, "data")
    return ptd
