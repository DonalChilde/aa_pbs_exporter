from pathlib import Path

from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_data import parse_pbs_data
from aa_pbs_exporter.pbs_2022_01.models.raw import BidPackage
from aa_pbs_exporter.pbs_2022_01.parser.parse_manager import ParseManager


def parse_pbs_file(
    file_path: Path,
    manager: ParseManager[BidPackage],
) -> BidPackage:
    with open(file_path, encoding="utf-8") as file_in:
        parse_pbs_data(strings=file_in, manager=manager)
    data = manager.result_handler().result_data()
    assert data is not None
    return data
