from dataclasses import dataclass
from pathlib import Path
from importlib import resources

from aa_pbs_exporter.snippets.parsing.parse_context import (
    DevParseContext,
    NoOpParseContext,
)
from aa_pbs_exporter.snippets.parsing.state_parser import Parser


@dataclass
class ParseTestingData:
    name: str
    source_txt: Path
    raw_parse_json: Path | None
    parse_json: Path | None
    extra: dict | None = None


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


def run_line_test(
    name: str, output_dir: Path, test_data: list, expected_state: str, parser: Parser
):
    output_path = output_dir / Path("lines") / f"{name}.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ctx = NoOpParseContext(source_name=name)
    with open(output_path, mode="w", encoding="utf-8") as fp_out:
        dev_ctx = DevParseContext(source_name=name, fp_out=fp_out, wrapped_context=ctx)
        for data in test_data:
            state = parser.parse(data.source, dev_ctx)
            assert state == expected_state
            assert data == dev_ctx.result
