from pathlib import Path

from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_strings import parse_pbs_strings
from aa_pbs_exporter.pbs_2022_01.models.raw import BidPackage
from aa_pbs_exporter.pbs_2022_01.parser.parse_manager import ParseManager


def parse_pbs_file(
    file_path: Path,
    manager: ParseManager[BidPackage],
) -> BidPackage:
    with open(file_path, encoding="utf-8") as file_in:
        data = parse_pbs_strings(strings=file_in, manager=manager)
    assert data is not None
    return data
