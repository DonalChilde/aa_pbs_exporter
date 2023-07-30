from importlib import resources
from logging import Logger
from pathlib import Path

from aa_pbs_exporter.pbs_2022_01.helpers.serialize_json import SerializeJson
from aa_pbs_exporter.pbs_2022_01.helpers.serialize_pydantic import SerializePydantic
from aa_pbs_exporter.pbs_2022_01.models import compact
from aa_pbs_exporter.pbs_2022_01.models import collated as raw
from aa_pbs_exporter.pbs_2022_01.validate.compact import (
    validate_compact_bid_package,
)
from tests.aa_pbs_exporter.resources.resource_definitions import COLLECTED_1, COMPACT_1


def test_compact_validation(test_app_data_dir: Path, logger: Logger):
    raw_bid_package_res = COLLECTED_1
    compact_bid_package_res = COMPACT_1
    output_path = test_app_data_dir / "validate-compact"
    with resources.as_file(raw_bid_package_res.file_resource()) as raw_path:
        raw_loader = SerializeJson[raw.BidPackage]("BidPackage")
        raw_bid_package = raw_loader.load_json(raw_path)
        debug_path = output_path / f"{raw_path.stem}-validate-debug.txt"
    with resources.as_file(compact_bid_package_res.file_resource()) as compact_path:
        compact_loader = SerializePydantic[compact.BidPackage]()
        compact_bid_package = compact_loader.load_json(
            compact.BidPackage, file_in=compact_path
        )
    validate_compact_bid_package(
        raw_bid_package=raw_bid_package,
        compact_bid_package=compact_bid_package,
        debug_file=debug_path,
    )

    # assert False
