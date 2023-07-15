from logging import Logger
from pathlib import Path
from aa_pbs_exporter.pbs_2022_01.helpers.serialize_pydantic import SerializePydantic
from tests.aa_pbs_exporter.pbs_2022_01.translate.resource_definitions import COLLECTED_1
from aa_pbs_exporter.pbs_2022_01.translate.collected_to_compact import (
    CollectedToCompact,
)
from aa_pbs_exporter.pbs_2022_01.helpers.serialize_json import SerializeJson
from aa_pbs_exporter.pbs_2022_01.models.raw_collected import BidPackage
from aa_pbs_exporter.pbs_2022_01.models import compact
from importlib import resources
from aa_pbs_exporter.pbs_2022_01.helpers.tz_from_iata import tz_from_iata
from tests.aa_pbs_exporter.resources.helpers_3 import ResourceLocator


def test_collected_to_compact(test_app_data_dir: Path, logger: Logger):
    input_resource = COLLECTED_1
    output_path = test_app_data_dir / "translate" / "collected-to-compact"
    with resources.as_file(input_resource.file_resource()) as input_path:
        loader = SerializeJson[BidPackage]("BidPackage")
        input_data = loader.load_from_json_file(input_path)
        debug_path = output_path / f"{input_path.stem}-compact-debug.txt"
        compact_path = output_path / f"{input_path.stem}-compact.json"
    translator = CollectedToCompact(
        tz_lookup=tz_from_iata, debug_file=debug_path, validator=None
    )
    with translator:
        compact_data = translator.translate(input_data)
        pydantic_serializer = SerializePydantic[compact.BidPackage]()
        pydantic_serializer.save_as_json(compact_path, compact_data)
    expected_res = ResourceLocator(
        f"{__package__}.resources.compact", f"{compact_path.name}"
    )
    with resources.as_file(expected_res.file_resource()) as expected_path:
        expected = pydantic_serializer.load_from_json_file(
            compact.BidPackage, expected_path
        )
    assert expected == compact_data
    # assert False
