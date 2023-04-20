from pathlib import Path

from tests.aa_pbs_exporter.conftest import resource_line_reader

from aa_pbs_exporter.airports.airports import tz_name_from_iata
from aa_pbs_exporter.pbs_2022_01.compact_to_expanded import (
    Translator as CompactTranslator,
)
from aa_pbs_exporter.pbs_2022_01.helpers import parse_raw_bidpackage
from aa_pbs_exporter.pbs_2022_01.parse_manager import ParseManager
from aa_pbs_exporter.pbs_2022_01.raw_to_compact import Translator as RawTranslator
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out


def test_raw_to_expanded(test_app_data_dir: Path):
    outpath = test_app_data_dir / "compact_to_expanded" / "three_pages"
    resource_package = "tests.aa_pbs_exporter.resources.data_2022.three_pages.data"
    resource_name = "source.txt"
    manager = ParseManager(ctx={})
    lines = resource_line_reader(resource_package, resource_name)
    raw_package = parse_raw_bidpackage(
        strings=lines, manager=manager, source="three_pages"
    )
    raw_json_path = outpath / f"{raw_package.default_file_name()}.json"
    validate_file_out(raw_json_path)
    raw_json_path.write_text(raw_package.json(indent=2))
    raw_translator = RawTranslator(tz_name_from_iata)
    compact_package = raw_translator.translate(raw_package)
    compact_json_path = outpath / f"{compact_package.default_file_name()}.json"
    validate_file_out(compact_json_path)
    compact_json_path.write_text(compact_package.json(indent=2))
    compact_translator = CompactTranslator()
    expanded_package = compact_translator.translate(compact_package)
    expanded_json_path = outpath / f"{expanded_package.default_file_name()}.json"
    validate_file_out(expanded_json_path)
    expanded_json_path.write_text(expanded_package.json(indent=2))
