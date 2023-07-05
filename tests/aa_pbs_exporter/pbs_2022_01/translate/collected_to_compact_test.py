from logging import Logger
from pathlib import Path
from tests.aa_pbs_exporter.pbs_2022_01.translate.resource_definitions import COLLECTED_1
from aa_pbs_exporter.pbs_2022_01.translate.collected_to_compact import (
    CollectedToCompact,
)
from aa_pbs_exporter.pbs_2022_01.helpers.serialize_json import SerializeJson
from aa_pbs_exporter.pbs_2022_01.models.raw_collected import BidPackage
from importlib import resources
from aa_pbs_exporter.pbs_2022_01.helpers.tz_from_iata import tz_from_iata


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
        # TODO make serializer for pydantic
