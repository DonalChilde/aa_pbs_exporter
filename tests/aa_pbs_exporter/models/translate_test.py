import importlib
import logging
from dataclasses import asdict
from datetime import date, datetime
from pprint import PrettyPrinter
from typing import List

import pytest
from tests.aa_pbs_exporter.conftest import PackageResource

from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.models.raw_2022_10.translate import (
    translate_package,
)
from aa_pbs_exporter.parser import parser_2022_10 as parser
from aa_pbs_exporter.util.state_parser import parse_file, parse_lines

pp = PrettyPrinter(indent=2, compact=True)
#####

TEST_STRING = """
   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/
DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SEQ 16942   1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU
                RPT 0930/0930                                                          −− −− −− −− −− −− −−
1  1/1 64 1492  DFW 1030/1030  L SJD 1225/1325   2.55          1.00                    −− −− 11 −− −− −− −−
1  1/1 64 1492  SJD 1325/1425    DFW 1712/1712   2.47          1.46X                   −− −− −− −− −− −− −−
1  1/1 63 1931  DFW 1858/1858  D ELP 1943/2043   1.45                                  −− −− −− −− −− −− −−
                                 RLS 1958/2058   7.27   0.00   7.27  11.28       11.13 −− −− −−
                ELP WYNDHAM EL PASO ARPT                    19157784241    11.32
                    SHUTTLE
                RPT 0730/0830
2  2/2 63 2218  ELP 0830/0930    DFW 1116/1116   1.46          1.38X
2  2/2 63 1785  DFW 1254/1254  L MSY 1422/1422   1.28
                                 RLS 1437/1437   3.14   0.00   3.14   6.07        5.52
                MSY HYATT REGENCY                           15045611234    15.23
                    ACADIA COACH LINES                      5043821487
                RPT 0600/0600
3  3/3 63 1266  MSY 0700/0700    CLT 1005/0905   2.05          1.05
3  3/3 63 2935  CLT 1110/1010  L SAN 1310/1510   5.00
                                 RLS 1325/1525   7.05   0.00   7.05   9.25        9.10
                SAN SHERATON MARINA                         16192912900    15.50
                    SHUTTLE
                RPT 0515/0715
4  4/4 64 2535  SAN 0615/0815  B DFW 1120/1120   3.05
                                 RLS 1135/1135   3.05   0.00   3.05   4.20        4.05
TTL                                             20.51   0.19  21.10        74.05
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SEQ 16943   1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU
                RPT 0936/0936                                                          −− −− −− −− −− −− −−
1  1/1 92 1161  DFW 1036/1036  L SLP 1242/1242   2.06                                  −− −− 11 −− −− −− −−
                                 RLS 1257/1257   2.06   0.00   2.06   3.21        3.06 −− −− −− −− −− −− −−
                SLP FIESTA AMERICANA SAN LUIS POTOSÃ-       524448801000   16.33       −− −− −− −− −− −− −−
                    SHUTTLE                                                            −− −− −−
                RPT 0530/0530
2  2/2 92  809  SLP 0630/0630    DFW 0855/0855   2.25          1.41X
2  2/2 92 1161  DFW 1036/1036  L SLP 1242/1242   2.06
                                 RLS 1257/1257   4.31   0.00   4.31   7.27        7.12
                SLP FIESTA AMERICANA SAN LUIS POTOSÃ-       524448801000   16.33
                    SHUTTLE
                RPT 0530/0530
3  3/3 92  809  SLP 0630/0630    DFW 0855/0855   2.25          1.41X
3  3/3 92 1161  DFW 1036/1036  L SLP 1242/1242   2.06
                                 RLS 1257/1257   4.31   0.00   4.31   7.27        7.12
                SLP FIESTA AMERICANA SAN LUIS POTOSÃ-       524448801000   16.08
                    SHUTTLE
                RPT 0505/0505
4  4/4 92  809  SLP 0605/0605    DFW 0830/0830   2.25          1.50X
4  4/4 29 2439  DFW 1020/1020  B OKC 1124/1124   1.04          0.46
4  4/4 29 2439  OKC 1210/1210    DFW 1315/1315   1.05
                                 RLS 1330/1330   4.34   0.00   4.34   8.25        8.10
TTL                                             15.42   5.59  21.41        75.54
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SEQ 16944   1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
                RPT 0948/0948                                                          −− −− −− −− −− −− −−
1  1/1 64 1821  DFW 1048/1048  L ONT 1159/1359   3.11          0.55                    −− −− 11 −− −− −− −−
1  1/1 64 1821  ONT 1254/1454    DFW 1750/1750   2.56          2.05X                   −− −− −− −− −− −− −−
1  1/1 26 1119  DFW 1955/1955    AUS 2056/2056   1.01                                  −− −− −− −− −− −− −−
                                 RLS 2111/2111   7.08   0.00   7.08  11.23       11.08 −− −− −−
                AUS AT&T HOTEL                              15124041900    17.17
                    J & G’S CITYWIDE EXPRESS                5127868131
                RPT 1428/1428
2  2/2 29 1083D AUS 1458/1458    PHX 1530/1730    AA    2.32   1.30X
2  2/2 26 2514  PHX 1700/1900    DFW 2122/2122   2.22
                                 RLS 2137/2137   2.22   2.32   4.54   7.09        6.54
TTL                                              9.30   2.32  12.02        35.49
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SEQ 16945   1 OPS   POSN CA FO                SPECIAL QUALIFICATION                    MO TU WE TH FR SA SU
                RPT 0953/0953                                                          −− −− −− −− −− −− −−
1  1/1 91 1390  DFW 1053/1053  L EGE 1207/1307   2.14          0.41                    −− −− 11 −− −− −− −−
1  1/1 91 1390  EGE 1248/1348    DFW 1554/1554   2.06                                  −− −− −− −− −− −− −−
                                 RLS 1609/1609   4.20   0.00   4.20   6.16        6.01 −− −− −− −− −− −− −−
TTL                                              4.20   0.55   5.15         6.16       −− −− −−
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−

COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               DFW 320  DOM                              PAGE   341"""


@pytest.fixture(scope="module", name="parsed_bid_page")
def parsed_bid_page_fixture() -> raw.Page:
    ctx = parser.ParseContext("Test string")
    scheme = parser.ParseScheme()
    lines = TEST_STRING.split("\n")
    parse_lines(lines, scheme, ctx, skipper=parser.make_skipper())
    page = ctx.bid_package.pages[-1]
    _ = asdict
    # pp.pprint(asdict(page))
    # pp.pprint(page)
    # print(page)
    return page


# def test_extract_calendar_entries(parsed_bid_page: raw.Page, logger: logging.Logger):
#     _ = logger
#     expected = "−− −− −− −− −− −− −− −− −− 11 −− −− −− −− −− −− −− −− −− −− −− −− −− −− −− −− −− −− −− −− −−".split()
#     for trip in parsed_bid_page.trips:
#         entries = extract_calendar_entries(trip)
#         assert expected == entries
#     # assert False


# def test_expand_from_to():
#     effective = datetime.strptime("02MAY2022", "%d%b%Y")
#     from_to = "05/02−06/01"
#     from_date, to_date = expand_from_to(effective, from_to)
#     assert datetime(year=2022, month=5, day=2) == from_date
#     assert datetime(year=2022, month=6, day=1) == to_date


# def test_days_in_range():
#     effective = datetime.strptime("02MAY2022", "%d%b%Y")
#     from_to = "05/02−06/01"
#     from_date, to_date = expand_from_to(effective, from_to)
#     days = days_in_range(from_date, to_date)
#     assert days == 31


# def test_extract_start_dates(parsed_bid_page: raw.Page):
#     effective = datetime.strptime(parsed_bid_page.page_footer.effective, "%d%b%Y")
#     for trip in parsed_bid_page.trips:
#         start_dates = extract_start_dates(
#             trip, effective, parsed_bid_page.page_header_2.calendar_range
#         )
#         assert len(start_dates) == 1
#         assert start_dates == [datetime(year=2022, month=5, day=11)]


def test_slice():
    effective = datetime.strptime("02MAY2022", "%d%b%Y")
    effective_date = effective.date()
    assert effective_date == date(year=2022, month=5, day=2)
    from_to = "05/02−06/01"
    from_md = from_to[:5]
    to_md = from_to[6:]
    assert from_md == "05/02"
    assert to_md == "06/01"
    parsed = datetime.strptime(f"{from_md}/{effective_date.year}", "%m/%d/%Y")
    from_date = parsed.date()
    assert from_date == date(year=2022, month=5, day=2)
    parsed = datetime.strptime(f"{to_md}/{effective_date.year}", "%m/%d/%Y")
    to_date = parsed.date()
    assert to_date == date(year=2022, month=6, day=1)


@pytest.fixture(scope="module", name="parsed_bid_package")
def parse_package(pairing_text_files: List[PackageResource]):
    ctx = parse_city("LAX", pairing_text_files)
    return ctx.bid_package


def parse_city(
    city: str, pairing_text_files: List[PackageResource]
) -> parser.ParseContext:
    scheme = parser.ParseScheme()
    for resource in [x for x in pairing_text_files if city in x.name]:
        with importlib.resources.path(resource.package, resource.name) as file_path:
            ctx = parser.ParseContext(str(file_path))
            parse_file(file_path, scheme=scheme, ctx=ctx, skipper=parser.make_skipper())
            return ctx


# def test_collect_airports(parsed_bid_package: raw.Package):
#     airports = collect_airports(parsed_bid_package)
#     print(airports)
#     assert len(airports) > 5
#     # assert False


def test_translate_package(parsed_bid_package: raw.Package, caplog):
    caplog.set_level(logging.WARNING)
    aa_package = translate_package(parsed_bid_package, source="tests")
    assert len(aa_package.trips) > 5
