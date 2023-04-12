from dataclasses import dataclass
from pathlib import Path

from tests.aa_pbs_exporter.resources.test_data_helpers import (
    compare_expected_and_result,
    get_results,
)

from aa_pbs_exporter.pbs_2022_01 import expand
from aa_pbs_exporter.pbs_2022_01.models import expanded, raw
from aa_pbs_exporter.pbs_2022_01.models.raw import IndexedString


@dataclass
class TestData:
    name: str
    description: str
    data: raw.Transportation | raw.TransportationAdditional


test_data = [
    TestData(
        name="transportation",
        description="",
        data=raw.Transportation(
            source=IndexedString(
                idx=1,
                txt="                    SIN FIN DE SERVICIOS                    3331223240",
            ),
            name="SIN FIN DE SERVICIOS",
            phone="3331223240",
            calendar="",
        ),
    ),
    TestData(
        name="transportation_additional",
        description="",
        data=raw.TransportationAdditional(
            source=IndexedString(
                idx=1,
                txt="                    SKY TRANSPORTATION SERVICE, LLC         8566169633",
            ),
            name="SKY TRANSPORTATION SERVICE, LLC",
            phone="8566169633",
            calendar="",
        ),
    ),
]
expected_result = {
    "transportation": expanded.Transportation(
        name="SIN FIN DE SERVICIOS", phone="3331223240"
    ),
    "transportation_additional": expanded.Transportation(
        name="SKY TRANSPORTATION SERVICE, LLC", phone="8566169633"
    ),
}


def test_all(test_app_data_dir: Path):
    output_path = test_app_data_dir / "expand" / "transportation"
    results = get_results(
        test_data=test_data, result_func=process_data, output_path=output_path
    )
    compare_expected_and_result(
        test_data=test_data, expected_results=expected_result, results=results
    )


def process_data(data) -> expanded.Transportation | None:
    result = expand.expand_transportation(data)
    return result
