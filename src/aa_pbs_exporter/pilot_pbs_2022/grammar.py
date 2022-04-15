from datetime import date, datetime, timedelta

import pyparsing as pp

# """
# COCKPIT  ISSUED 03SEP2021  EFF 01OCT2021               PHX 320  INTL                             PAGE  2205
# """


def short_string_to_date(s: str, loc: int, tocs: pp.ParseResults):
    return datetime.strptime(tocs[0][0], "%m%b%Y").date()


def string_to_time(s: str, loc: int, tocs: pp.ParseResults):
    return datetime.strptime(tocs[0], "%H%M").time()


def duration_to_timedelta(s: str, loc: int, tocs: pp.ParseResults):
    return timedelta(hours=int(tocs[0]["hours"]), minutes=int(tocs[0]["minutes"]))


def string_to_int(s: str, loc: int, tocs: pp.ParseResults):
    return int(tocs[0])


DAY_NUMERAL = pp.Word(pp.nums, exact=2)("day").set_parse_action(string_to_int)
SHORT_MONTH = pp.Word(pp.alphas, exact=3)("month")
MONTH_NUMERAL = pp.Word(pp.nums, exact=2)("month").set_parse_action(string_to_int)
YEAR = pp.Word(pp.nums, exact=4)("year").set_parse_action(string_to_int)
DATE = pp.Combine(DAY_NUMERAL + SHORT_MONTH + YEAR).set_parse_action(
    short_string_to_date
)
TIME = pp.Combine(pp.Word(pp.nums, exact=2) + pp.Word(pp.nums, exact=2)).setParseAction(
    string_to_time
)
MONTH_DAY = MONTH_NUMERAL + "/" + DAY_NUMERAL
BASE = pp.Word(pp.alphas, exact=3)("base")
EQUIPMENT = pp.Word(pp.nums, exact=3)("equipment")
DIVISION = pp.Literal("INTL") | pp.Literal("DOM")
SEQ_NUMBER = pp.Word(pp.nums, min=1)("seq_number")
OPS = pp.Word(pp.nums, min=1)("ops").set_parse_action(string_to_int)
POSITIONS = pp.one_of("CA FO", as_keyword=True)
CALENDAR_HEADER = pp.Literal("MO") + "TU" + "WE" + "TH" + "FR" + "SA" + "SU"
CALENDAR_ENTRY = pp.Or(
    [
        pp.Word("-", exact=2, as_keyword=True),
        pp.Word(pp.nums, exact=1, as_keyword=True).set_parse_action(string_to_int),
        pp.Word(pp.nums, exact=2, as_keyword=True).set_parse_action(string_to_int),
    ]
)
DUTY_PERIOD = pp.Word(pp.nums, exact=1)("duty_period").set_parse_action(string_to_int)
EQUIPMENT_CODE = pp.Word(pp.nums, exact=2, as_keyword=True)
DAY_OF_SEQUENCE = pp.Group(
    pp.Word(pp.nums, exact=1).set_parse_action(string_to_int)("d")
    + "/"
    + pp.Word(pp.nums, exact=1).set_parse_action(string_to_int)("a")
)("day_of_sequence")
FLIGHT_NUMBER = pp.Word(pp.nums, as_keyword=True)("flight_number")
CITY_CODE = pp.Word(pp.alphas, exact=3, as_keyword=True)
CREW_MEAL = pp.Word("BLD", exact=1, as_keyword=True)
DURATION = pp.Combine(
    pp.Word(pp.nums, min=1)("hours") + "." + pp.Word(pp.nums, exact=2)("minutes")
).set_parse_action(duration_to_timedelta)
PHONE_NUMBER = pp.Combine(pp.Word(pp.nums, min=4, as_keyword=True))
# COCKPIT  ISSUED 03SEP2021  EFF 01OCT2021               PHX 320  INTL                             PAGE  2205
FOOTER = (
    pp.StringStart()
    + "COCKPIT"
    + "ISSUED"
    + DATE("issued")
    + "EFF"
    + DATE("effective")
    + BASE
    + EQUIPMENT
    + DIVISION("division")
    + "PAGE"
    + pp.Word(pp.nums)("internal_page")
    + pp.StringEnd()
)
#   DAY          --DEPARTURE--    ---ARRIVAL---                GRND/        REST/
HEADER_1 = (
    pp.StringStart()
    + "DAY"
    + "--DEPARTURE--"
    + "---ARRIVAL---"
    + "GRND/"
    + "REST/"
    + pp.StringEnd()
)
# DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 10/01-10/31
HEADER_2 = (
    pp.StringStart()
    + "DP"
    + "D/A"
    + "EQ"
    + "FLT#"
    + "STA"
    + "DLCL/DHBT"
    + "ML"
    + "STA"
    + "ALCL/AHBT"
    + "BLOCK"
    + "SYNTH"
    + "TPAY"
    + "DUTY"
    + "TAFB"
    + "FDP"
    + "CALENDAR"
    + pp.Group(MONTH_DAY)("calendar_from")
    + "-"
    + pp.Group(MONTH_DAY)("calendar_to")
    + pp.StringEnd()
)
# -----------------------------------------------------------------------------------------------------------
SEPARATOR = pp.StringStart() + pp.Word("-", min=5) + pp.StringEnd()
# SEQ 8325    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
SEQ_HEADER = (
    pp.StringStart()
    + "SEQ"
    + SEQ_NUMBER
    + OPS
    + "OPS"
    + "POSN"
    + pp.OneOrMore(POSITIONS)("positions")
    + CALENDAR_HEADER
    + pp.StringEnd()
)
#                RPT 0600/0600                                                                      -- -- --
REPORT = (
    pp.StringStart()
    + "RPT"
    + TIME("report_local")
    + "/"
    + TIME("report_home")
    + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
    + pp.StringEnd()
)
# 1  1/1 63 2107  PHX 1530/1530    SNA 1653/1653   1.23          0.58                     4 -- -- -- -- -- --
FLIGHT = (
    pp.StringStart()
    + DUTY_PERIOD
    + DAY_OF_SEQUENCE
    + EQUIPMENT_CODE("equipment_code")
    + FLIGHT_NUMBER
    + CITY_CODE("departure_city")
    + TIME("departure_local")
    + "/"
    + TIME("departure_home")
    + pp.Opt(CREW_MEAL, default=None)("crew_meal")
    + CITY_CODE("arrival_city")
    + TIME("arrival_local")
    + "/"
    + TIME("arrival_home")
    + DURATION("block")
    + DURATION("total_pay")
    + pp.Opt("X")("equipment_change")
    + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
    + pp.StringEnd()
)
#                                 RLS 2202/2002   7.28   0.00   7.28  11.36       11.06 -- -- -- -- -- -- --
RELEASE = (
    pp.StringStart()
    + "RLS"
    + TIME("release_local")
    + "/"
    + TIME("release_home")
    + DURATION("block")
    + DURATION("synth")
    + DURATION("total_pay")
    + DURATION("duty")
    + DURATION("flight_duty")
    + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
    + pp.StringEnd()
)
#                ORD HYATT REGENCY ORD                       18476961234    16.03
#                DFW MARRIOTT DFW AP                         19729298800    13.31       -- -- -- -- -- -- --
#                SEA HOTEL INFO IN CCI/CREW PORTAL                          11.33
HOTEL = (
    pp.StringStart()
    + CITY_CODE("layover_city")
    + pp.original_text_for(
        pp.Opt(
            pp.OneOrMore(
                ~PHONE_NUMBER + ~DURATION + pp.Word(pp.printables, as_keyword=True)
            ),
            default=None,
        )
    )("hotel")
    + pp.Opt(~DURATION + PHONE_NUMBER, default=None)("hotel_phone")
    + DURATION("rest")
    + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
    + pp.StringEnd()
)
#                    SKYHOP GLOBAL                           9544000412                 -- -- -- -- -- -- 31
TRANSPORTATION = (
    pp.StringStart()
    + pp.original_text_for(
        pp.Opt(
            pp.OneOrMore(~PHONE_NUMBER + pp.Word(pp.printables, as_keyword=True)),
            default=None,
        )
    )("transportation")
    + pp.Opt(~CALENDAR_ENTRY + PHONE_NUMBER, default=None)("transportation_phone")
    + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
    + pp.StringEnd()
)
# TTL                                             21.33   0.00  21.33        73.59
TOTAL = (
    pp.StringStart()
    + "TTL"
    + DURATION("block")
    + DURATION("synth")
    + DURATION("total_pay")
    + DURATION("tafb")
    + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
    + pp.StringEnd()
)
# PHX 320
BASE_EQUIPMENT = (
    pp.StringStart() + CITY_CODE("base") + EQUIPMENT("equipment") + pp.StringEnd()
)
