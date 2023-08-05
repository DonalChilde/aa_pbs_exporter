"""Main entry point"""
from pathlib import Path
from typing import Any

from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_strings_td import pbs_data_filter
from aa_pbs_exporter.pbs_2022_01.helpers.serialize_json import SerializeJson
from aa_pbs_exporter.pbs_2022_01.models import collated, compact, expanded
from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme import parser_lookup
from aa_pbs_exporter.pbs_2022_01.translate import (
    translate_parsed_to_collated,
    translate_collated_to_compact,
    translate_compact_to_expanded,
)
from aa_pbs_exporter.pbs_2022_01.validate import (
    validate_compact_bid_package,
    validate_expanded_bid_package,
    validate_collated_bid_package,
)
from aa_pbs_exporter.snippets.hash.file_hash import make_hashed_file_dict
from aa_pbs_exporter.snippets.indexed_string.typedict.index_strings import Indexer
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_file import (
    parse_text_file,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
)

INDEXER = Indexer(sieve=pbs_data_filter(), index_start=1)


def load_collated(file_in: Path) -> collated.BidPackage:
    data = collated.load_json(file_in=file_in)
    return data


def save_collated(file_out: Path, bid_package: collated.BidPackage):
    collated.save_json(file_out=file_out, bid_package=bid_package)


def load_compact(file_in: Path) -> compact.BidPackage:
    data = compact.load_json(file_in=file_in)
    return data


def save_compact(file_out: Path, bid_package: compact.BidPackage):
    compact.save_json(file_out=file_out, bid_package=bid_package)


def load_expanded(file_in: Path) -> expanded.BidPackage:
    data = expanded.load_json(file_in=file_in)
    return data


def save_expanded(file_out: Path, bid_package: expanded.BidPackage):
    expanded.save_json(file_out=file_out, bid_package=bid_package)


def load_parse_results(file_in: Path) -> CollectedParseResults:
    serializer = SerializeJson[CollectedParseResults](
        data_type_name="CollectedParseResults"
    )
    return serializer.load_json(file_in=file_in)


def save_parse_results(file_out: Path, parse_results: CollectedParseResults):
    serializer = SerializeJson[CollectedParseResults](
        data_type_name="CollectedParseResults"
    )
    serializer.save_json(file_out=file_out, data=parse_results)


def parse_pbs_txt_file(
    file_in: Path, debug_file: Path | None, job_name: str, metadata: dict[str, Any]
) -> CollectedParseResults:
    local_metadata: dict[str, Any] = {}
    source = make_hashed_file_dict(file_path=file_in)
    local_metadata["source"] = source
    local_metadata.update(metadata)
    result = parse_text_file(
        file_in=file_in,
        debug_file=debug_file,
        job_name=job_name,
        parser_lookup=parser_lookup,
        indexer=Indexer(sieve=pbs_data_filter(), index_start=1),
    )

    result["metadata"].update(local_metadata)
    return result


def parsed_to_collated(
    parse_results: CollectedParseResults, debug_file: Path | None
) -> collated.BidPackage:
    collated_bid_package = translate_parsed_to_collated(
        parse_results=parse_results, debug_file=debug_file
    )
    validate_collated_bid_package(
        parse_results=parse_results,
        bid_package=collated_bid_package,
        debug_file=debug_file,
    )
    return collated_bid_package


def collated_to_compact(
    bid_package: collated.BidPackage, debug_file: Path | None
) -> compact.BidPackage:
    compact_bid_package = translate_collated_to_compact(
        collated_bid_package=bid_package, debug_file=debug_file
    )
    validate_compact_bid_package(
        raw_bid_package=bid_package,
        compact_bid_package=compact_bid_package,
        debug_file=debug_file,
    )
    return compact_bid_package


def compact_to_expanded(
    bid_package: compact.BidPackage, debug_file: Path | None
) -> expanded.BidPackage:
    expanded_bid_package = translate_compact_to_expanded(
        compact_package=bid_package, debug_file=debug_file
    )
    validate_expanded_bid_package(
        compact_bid_package=bid_package,
        expanded_bid_package=expanded_bid_package,
        debug_file=debug_file,
    )
    return expanded_bid_package
