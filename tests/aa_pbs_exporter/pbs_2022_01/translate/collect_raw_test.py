from importlib import resources
from logging import Logger
from pathlib import Path

from aa_pbs_exporter.pbs_2022_01.helpers.serialize_json import SerializeJson
from aa_pbs_exporter.pbs_2022_01.models.raw_collected import BidPackage
from aa_pbs_exporter.pbs_2022_01.translate.collect_raw import collect_raw
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
)
from tests.aa_pbs_exporter.pbs_2022_01.translate.resource_definitions import COLLECTED_1


def test_collect_raw(test_app_data_dir: Path, logger: Logger):
    input_res = COLLECTED_1
    with resources.as_file(input_res.file_resource()) as input_path:
        output_path = test_app_data_dir / "collect_raw" / f"{input_path.stem}.json"
        input_serializer = SerializeJson[CollectedParseResults]("CollectedParseResults")
        parse_results = input_serializer.load_from_json_file(input_path)
    output_serializer = SerializeJson[BidPackage]("BidPackage")
    bid_package = collect_raw(parse_results=parse_results)
    output_serializer.save_as_json(output_path, bid_package)
    assert len(bid_package["pages"]) == 3
