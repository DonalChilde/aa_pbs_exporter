import logging
from pathlib import Path

from tests.aa_pbs_exporter.resources.data_2022.lax_777_intl.fixtures import (
    lax_777_intl_fixture,
)
from tests.aa_pbs_exporter.resources.data_2022.three_pages.fixtures import (
    three_pages_fixture,
)
from tests.aa_pbs_exporter.resources.helpers import ParseTestingData

from aa_pbs_exporter.models.raw_2022_10.bid_package import Package
from aa_pbs_exporter.models.raw_2022_10.validate import validate_bid_package
from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext
from aa_pbs_exporter.snippets.parsing.state_parser import parse_lines

_ = lax_777_intl_fixture, three_pages_fixture


def test_lax_777_intl(logger, lax_777_intl: ParseTestingData, test_app_data_dir: Path):
    parse_data = lax_777_intl
    output_path = test_app_data_dir / f"{parse_data.name}.txt"
    ctx = line_parser.LineParseContext(parse_data.name)
    scheme = line_parser.ParseScheme()
    lines = parse_data.source_txt.read_text().split("\n")
    with open(output_path, mode="w", encoding="utf-8") as fp_out:
        dev_ctx = DevParseContext(
            source_name=ctx.source_name, fp_out=fp_out, wrapped_context=ctx
        )
        parse_lines(lines, scheme, dev_ctx, skipper=line_parser.make_skipper())
    bid_package: Package = dev_ctx.wrapped_context.results_obj  # type: ignore
    validate_bid_package(bid_package, ctx)
    page = bid_package.pages[-1]
    assert page.trips[-1].header.number == "683"
    assert page.trips[-2].dutyperiods[0].layover is not None
    assert page.trips[-2].dutyperiods[0].layover.hotel.name == "COURTYARD CENTRAL PARK"
    assert page.trips[-2].dutyperiods[0].layover.transportation is not None
    assert page.trips[-2].dutyperiods[0].layover.transportation.name == "DESERT COACH"
    # debug(page.trips[0])
    # assert False


def test_three_pages(logger, three_pages: ParseTestingData, test_app_data_dir: Path):
    parse_data = three_pages
    output_path = test_app_data_dir / f"{parse_data.name}.txt"
    ctx = line_parser.LineParseContext(parse_data.name)
    scheme = line_parser.ParseScheme()
    lines = parse_data.source_txt.read_text().split("\n")
    with open(output_path, mode="w", encoding="utf-8") as fp_out:
        dev_ctx = DevParseContext(
            source_name=ctx.source_name, fp_out=fp_out, wrapped_context=ctx
        )
        parse_lines(lines, scheme, dev_ctx, skipper=line_parser.make_skipper())
    bid_package: Package = dev_ctx.wrapped_context.results_obj  # type: ignore
    assert len(bid_package.pages) == 3
