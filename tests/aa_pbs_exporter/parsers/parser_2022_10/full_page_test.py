import logging

from tests.aa_pbs_exporter.resources.data_2022.lax_777_intl.fixtures import (
    _lax_777_intl,
)
from tests.aa_pbs_exporter.resources.helpers import ParseTestingData

from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.util.state_parser import parse_lines

_ = _lax_777_intl


def test_page(logger: logging.Logger, lax_777_intl: ParseTestingData):
    ctx = line_parser.ParseContext("Test string")
    scheme = line_parser.ParseScheme()
    lines = lax_777_intl.source_txt.read_text().split("\n")
    parse_lines(lines, scheme, ctx, skipper=line_parser.make_skipper())
    page = ctx.bid_package.pages[-1]
    assert page.trips[-1].header.number == "683"
    assert page.trips[-2].dutyperiods[0].layover.hotel.name == "COURTYARD CENTRAL PARK"
    assert page.trips[-2].dutyperiods[0].layover.transportation.name == "DESERT COACH"
    # assert False
