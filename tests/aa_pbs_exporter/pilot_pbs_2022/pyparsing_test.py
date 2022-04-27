import re
from concurrent.futures.process import _ResultItem

import pyparsing as pp
from pfmsoft.text_chunk_parser import StringChunkProvider

from aa_pbs_exporter.pilot_pbs_2022 import parser

TRANS = """
                    J & G’S CITYWIDE EXPRESS                5127868131
                    TRANS INFO IN CCI/CREW PORTAL                                      −− −−  1
                    COMET CAR HIRE (CCH) LTD                442088979984               −− −− −−
"""


def test_unicode_quote():
    test_string = "G’S"
    replaced = test_string.replace("\u2019", "'")
    print("replace", replaced)

    parser = pp.Word(pp.printables + "\u2019")
    result = parser.parse_string(test_string)
    print(result)
    assert False


def test_flight():
    pp.enable_all_warnings()
    text = "1  1/1 45  435D MIA 1010/1010    CLT 1225/1225    AA    2.15                           −− −− −− −− −− −− −−\n"
    text_2 = "1  1/1 45  435D MIA 1010/1010    CLT 1225/1225    0.00    2.15                           −− −− −− −− −− −− −−\n"
    text_3 = "1  1/1 45 2250D BOS 1429/1429    CLT 1657/1657    AA    2.28   1.42X                   −− −− −− −− −− −− −−\n"
    foo = parser.FlightLine()._define_parser().set_debug()
    result = foo.parse_string(text_3)
    print(result.dump())
    assert False


def test_duration():
    text = "2.30"
    dur = parser.DURATION("name")
    result = dur.parseString(text)
    print(result)
    bare = pp.Combine(
        pp.Word(pp.nums, min=1)("hours") + "." + pp.Word(pp.nums, exact=2)("minutes")
    ).set_parse_action(parser.duration_to_timedelta_2)("dur")
    result = bare.parseString(text)
    print(result.dump())
    print(result.as_dict())
    assert False


def test_flight_with_deadhead():
    text = "1  1/1 45 2250D BOS 1429/1429    CLT 1657/1657    AA    2.28   1.42X                   −− −− −− −− −− −− −−\n"
    flight_with_deadhead = r"^(?P<duty_period>\d)\s*(?P<d_day>\d)\/(?P<a_day>\d)\s*(?P<equipment>\d{2})\s*(?P<flight_number>\d{1,4})(?P<deadhead>[D])?\s*(?P<departure_city>\w{3})\s*(?P<departure_local>\d{4})\/(?P<departure_hbt>\d{4})\s*(?P<crewmeal>\w)?\s*(?P<arrival_city>\w{3})\s*(?P<arrival_local>\d{4})\/(?P<arrival_hbt>\d{4})\s*(?P<deadhead_block>AA)\s*(?P<synth>\d{1,2}\.\d{2})\s*(?P<ground>\d{1,2}\.\d{2})?(?P<equipment_change>X)?\s*(?P<calendar>[−\s\d]*)\n$"
    pattern = re.compile(flight_with_deadhead)
    match = pattern.match(text)
    print(match.groupdict())
    assert False


def test_flight_without_deadhead():
    text = "    2  2/2 26 2112  DFW 0600/0700  B LAX 0725/1025   3.25          2.35X\n"
    flight_with_deadhead = r"^(?P<duty_period>\d)\s*(?P<d_day>\d)\/(?P<a_day>\d)\s*(?P<equipment>\d{2})\s*(?P<flight_number>\d{1,4})(?P<deadhead>[D])?\s*(?P<departure_city>\w{3})\s*(?P<departure_local>\d{4})\/(?P<departure_hbt>\d{4})\s*(?P<arrival_city>\w{3})\s*(?P<arrival_local>\d{4})\/(?P<arrival_hbt>\d{4})\s*(?P<deadhead_block>AA)\s*(?P<synth>\d{1,2}\.\d{2})\s*(?P<ground>\d{1,2}\.\d{2})?(?P<equipment_change>X)?\s*(?P<calendar>[−\s\d]*)\n$"
    pattern = re.compile(flight_with_deadhead)
    match = pattern.match(text)
    print(match.groupdict())
    assert False


def test_string_concat():
    FOO = "foo"
    BAR = "bar"
    FOOBAR = "foo" "bar"
