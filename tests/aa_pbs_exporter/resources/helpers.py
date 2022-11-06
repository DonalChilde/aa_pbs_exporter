from dataclasses import dataclass
from pathlib import Path
from importlib import resources


@dataclass
class ParseTestingData:
    source_txt: Path
    raw_parse_json: Path | None
    parse_json: Path | None
    extra: dict | None = None


def parent_package_path(package: str) -> str:
    split_path = package.split(".")
    split_path.pop()
    return ".".join(split_path)


def build_testing_data(package_parent: str, package: str) -> ParseTestingData:
    with resources.path(package=package_parent, resource=package) as root_path:
        source = root_path / "source.txt"
        raw_parse_json: Path | None = root_path / "raw_parse.json"
        parse_json: Path | None = root_path / "parse.json"
    if not source.is_file():
        raise ValueError(
            f"Source file {source} does not exist. {package_parent=} {package=}"
        )
    if not raw_parse_json.is_file:  # type: ignore
        raw_parse_json = None
    if not parse_json.is_file():  # type: ignore
        parse_json = None
    return ParseTestingData(
        source_txt=source, raw_parse_json=raw_parse_json, parse_json=parse_json
    )
