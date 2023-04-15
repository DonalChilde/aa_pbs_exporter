from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from aa_pbs_exporter.pbs_2022_01.helpers import parse_string_by_line
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.snippets.state_parser import state_parser_protocols as spp


@dataclass
class ParseTestingData:
    name: str
    source_txt: Path
    raw_parse_json: Path | None
    parse_json: Path | None
    extra: dict | None = None


class ParseTestData(BaseModel):
    name: str
    txt: str
    description: str


def parent_package_path(package: str) -> str:
    split_path = package.split(".")
    split_path.pop()
    return ".".join(split_path)


def build_testing_data(
    package_parent: str, package: str, name: str
) -> ParseTestingData:
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
        name=name,
        source_txt=source,
        raw_parse_json=raw_parse_json,
        parse_json=parse_json,
    )


def parse_lines(
    test_data: list[ParseTestData],
    result_data: dict[str, Any],
    parser: spp.IndexedStringParserProtocol,
    output_path: Path | None = None,
    skip_test: bool = False,
):
    collected_results = {}
    for idx, data in enumerate(test_data, start=1):
        result = parser.parse(raw.IndexedString(idx=idx, txt=data.txt), ctx={})
        if output_path:
            individual_outpath = output_path / f"{data.name}.py"
            output_results_repr(individual_outpath, result)
        if not skip_test:
            assert result == result_data[data.name], f"{data.name}: {data.description}"
        collected_results[data.name] = result
    if output_path:
        collected_outpath = output_path / "collected.py"
        output_results_repr(collected_outpath, collected_results)


def parse_pages(
    test_data: ParseTestData,
    bid_package: raw.BidPackage | None,
    output_path: Path | None = None,
    skip_test: bool = False,
):
    parsed_bid_package = parse_string_by_line(
        source=test_data.name, string_data=test_data.txt
    )
    if output_path:
        individual_outpath = output_path / f"{test_data.name}.py"
        output_results_repr(individual_outpath, parsed_bid_package)
    if not skip_test:
        assert (
            bid_package == parsed_bid_package
        ), f"{test_data.name}: {test_data.description}"


def output_results_repr(output_path: Path, results):
    output_txt = f"result_data = {repr(results)}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_txt)
