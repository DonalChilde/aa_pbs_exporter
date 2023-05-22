from importlib import resources
from logging import Logger
from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData

from aa_pbs_exporter.pbs_2022_01.parse_pbs_pdf_file import parse_pbs_pdf_file

SERIALIZE_ONLY = False
PDF_TEST_DATA = ResourceTestData(
    input_data="PBS_DCA_May_2022_20220408124308.pdf", result_data=""
)
RAW_TEST_DATA = ResourceTestData("", "one_page_raw.json")
COMPACT_TEST_DATA = ResourceTestData("", "one_page_compact.json")
EXPANDED_TEST_DATA = ResourceTestData("", "one_page_expanded.json")


@pytest.mark.slow
def test_pdf(test_app_data_dir: Path, logger: Logger):
    output_path = (
        test_app_data_dir
        / "pdf_package"
        / "dca_may_2022"
        / __name__.rsplit(".", maxsplit=1)[-1]
    )
    res_dir = resources.files(__package__)
    res_file = res_dir.joinpath(PDF_TEST_DATA.input_data)
    raw_package, compact_package, expanded_package = parse_pbs_pdf_file(
        pdf_file=res_file,
        output_dir=output_path,
    )
