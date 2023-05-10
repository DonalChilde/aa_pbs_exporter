from importlib import resources
from logging import Logger
from pathlib import Path

import pytest
from pydantic import parse_raw_as
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData

from aa_pbs_exporter.pbs_2022_01.models import compact, expanded, raw
from aa_pbs_exporter.pbs_2022_01.parse_pbs_txt_file import parse_pbs_txt_file

SERIALIZE_ONLY = False
PDF_TEST_DATA = ResourceTestData(
    input_data="PBS_DCA_May_2022_20220408124308.txt", result_data=""
)
RAW_TEST_DATA = ResourceTestData("", "02MAY2022_DCA_raw.json")
COMPACT_TEST_DATA = ResourceTestData("", "2022-05-02_2022-06-01_DCA_compact.json")
EXPANDED_TEST_DATA = ResourceTestData("", "2022-05-02_2022-06-01_DCA_expanded.json")


@pytest.mark.slow
def test_txt(test_app_data_dir: Path, logger: Logger):
    output_path = (
        test_app_data_dir
        / "txt_package"
        / "dca_may_2022"
        / __name__.rsplit(".", maxsplit=1)[-1]
    )
    res_dir = resources.files(__package__)
    res_file = res_dir.joinpath(PDF_TEST_DATA.input_data)
    raw_package, compact_package, expanded_package = parse_pbs_txt_file(
        txt_file=res_file,
        output_dir=output_path,
    )
    if not SERIALIZE_ONLY:
        input_bytes = res_dir.joinpath(RAW_TEST_DATA.result_data).read_bytes()
        raw_expected = parse_raw_as(raw.BidPackage, input_bytes)
        assert raw_expected == raw_package
        input_bytes = res_dir.joinpath(COMPACT_TEST_DATA.result_data).read_bytes()
        compact_expected = parse_raw_as(compact.BidPackage, input_bytes)
        assert compact_expected == compact_package
        input_bytes = res_dir.joinpath(EXPANDED_TEST_DATA.result_data).read_bytes()
        expanded_expected = parse_raw_as(expanded.BidPackage, input_bytes)
        assert expanded_expected == expanded_package
