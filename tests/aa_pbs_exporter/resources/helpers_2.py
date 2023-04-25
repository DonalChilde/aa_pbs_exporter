import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Iterable, Type, TypeVar

from pydantic import parse_obj_as
from pydantic.json import pydantic_encoder

from aa_pbs_exporter.pbs_2022_01.models.raw import IndexedString, ParsedIndexedString
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.pbs_2022_01.parsers import IndexedStringParser
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out

B = TypeVar("B", bound=ParsedIndexedString)


@dataclass
class ResourceTestData:
    input_data: str
    result_data: str
    description: str = ""


def parse_lines(
    line_data: Iterable[str], parser: IndexedStringParser, ctx: dict | None = None
) -> list[ParseResult]:
    """A convenience method for parsing lines of sample data.

    Assumes the same parser matches each line.
    """
    if ctx is None:
        ctx = {}
    results = []
    for idx, txt in enumerate(line_data):
        try:
            result = parser.parse(IndexedString(idx=idx, txt=txt), ctx=ctx)
        except Exception as error:
            # log it?
            print(error)
            raise error
        results.append(result)
    return results


def deserialize_parse_results(
    serialized_data: str, model: Type[B]
) -> list[ParseResult]:
    """Deserialize a json string into a list of ParseResults."""
    results = []
    data = json.loads(serialized_data)
    for item in data:
        deserialized_model = parse_obj_as(model, item["parsed_data"])
        results.append(
            ParseResult(
                current_state=item["current_state"], parsed_data=deserialized_model
            )
        )
    return results


def parse_lines_package_resource(
    resource_path: str, resource_name: str, parser
) -> list[ParseResult]:
    res_dir = resources.files(resource_path)
    res_file = res_dir.joinpath(resource_name)
    with res_file.open() as file:
        results = parse_lines(file, parser)
    return results


def load_parse_results_package_resource(
    resource_path: str, resource_name: str, model: Type[B]
) -> list[ParseResult]:
    res_dir = resources.files(resource_path)
    res_file = res_dir.joinpath(resource_name)
    return deserialize_parse_results(res_file.read_text(), model=model)


def serialize_parse_results(
    parse_results: list[ParseResult], output_dir: Path, file_name: str
):
    output_path = output_dir / file_name
    validate_file_out(output_path)
    output_path.write_text(
        json.dumps(parse_results, default=pydantic_encoder, indent=2)
    )


def process_lines(
    package: str,
    data: ResourceTestData,
    path_out: Path,
    parser,
    model,
    serialize_only: bool = False,
):
    results = parse_lines_package_resource(package, data.input_data, parser)
    serialize_parse_results(results, output_dir=path_out, file_name=data.result_data)
    if not serialize_only:
        loaded = load_parse_results_package_resource(
            resource_path=package, resource_name=data.result_data, model=model
        )
        assert results == loaded
