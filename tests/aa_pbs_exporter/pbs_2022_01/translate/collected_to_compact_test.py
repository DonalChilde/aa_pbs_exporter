from importlib import resources
from logging import Logger
from pathlib import Path

from aa_pbs_exporter.pbs_2022_01.helpers.serialize_json import SerializeJson
from aa_pbs_exporter.pbs_2022_01.helpers.serialize_pydantic import SerializePydantic
from aa_pbs_exporter.pbs_2022_01.models import compact
from aa_pbs_exporter.pbs_2022_01.models.collated import BidPackage
from aa_pbs_exporter.pbs_2022_01.translate.collated_to_compact import (
    translate_collated_to_compact,
)
from tests.aa_pbs_exporter.resources.resource_definitions import COLLECTED_1
from tests.aa_pbs_exporter.resources.helpers_3 import ResourceLocator


def test_collected_to_compact(test_app_data_dir: Path, logger: Logger):
    input_resource = COLLECTED_1
    output_path = test_app_data_dir / "translate" / "collected-to-compact"
    with resources.as_file(input_resource.file_resource()) as input_path:
        loader = SerializeJson[BidPackage]("BidPackage")
        input_data = loader.load_from_json_file(input_path)
        debug_path = output_path / f"{input_path.stem}-compact-debug.txt"
        compact_path = output_path / f"{input_path.stem}-compact.json"
    compact_bid = translate_collated_to_compact(
        collated_bid_package=input_data, debug_file=debug_path
    )

    pydantic_serializer = SerializePydantic[compact.BidPackage]()
    pydantic_serializer.save_json(compact_path, compact_bid)
    expected_res = ResourceLocator(
        f"{__package__}.resources.compact", f"{compact_path.name}"
    )
    with resources.as_file(expected_res.file_resource()) as expected_path:
        expected = pydantic_serializer.load_json(compact.BidPackage, expected_path)
    assert expected == compact_bid
    # assert False
