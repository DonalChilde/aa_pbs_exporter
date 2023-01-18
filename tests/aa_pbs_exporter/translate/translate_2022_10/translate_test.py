from tests.aa_pbs_exporter.resources.data_2022.lax_777_intl.fixtures import (
    lax_777_intl_fixture,
)
from tests.aa_pbs_exporter.resources.helpers import ParseTestingData
from aa_pbs_exporter.models.bid_package_2022_10.translate_2022_10 import (
    translate_package,
)

from aa_pbs_exporter.parsers.parser_2022_10 import line_parser
from aa_pbs_exporter.snippets.parsing.state_parser import parse_lines

_ = lax_777_intl_fixture


def test_page(logger, lax_777_intl: ParseTestingData):
    ctx = line_parser.LineParseContext("Test string")
    scheme = line_parser.ParseScheme()
    lines = lax_777_intl.source_txt.read_text().split("\n")
    parse_lines(lines, scheme, ctx, skipper=line_parser.make_skipper())
    page = ctx.results_obj.pages[-1]
    assert page.trips[-1].header.number == "683"
    assert page.trips[-2].dutyperiods[0].layover is not None
    assert page.trips[-2].dutyperiods[0].layover.transportation is not None
    assert page.trips[-2].dutyperiods[0].layover.hotel.name == "COURTYARD CENTRAL PARK"
    assert page.trips[-2].dutyperiods[0].layover.transportation.name == "DESERT COACH"
    translated = translate_package(bid_package=ctx.results_obj, source="lax_777_intl")
    print(translated)
    # assert False
