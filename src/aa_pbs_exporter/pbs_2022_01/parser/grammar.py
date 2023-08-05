import pyparsing as pp

CALENDAR_HEADER = pp.Literal("MO") + "TU" + "WE" + "TH" + "FR" + "SA" + "SU"
MONTH_NUMERAL = pp.Word(pp.nums, exact=2)
DAY_NUMERAL = pp.Word(pp.nums, exact=2)
SHORT_MONTH = pp.Word(pp.alphas, exact=3)
DATE_DDMMM = MONTH_NUMERAL + SHORT_MONTH
DATE_MM_SLASH_DD = MONTH_NUMERAL + "/" + DAY_NUMERAL
MINUS_SIGN = "\u2212"
HYPHEN_MINUS = "\u002d"
DASH_UNICODE = "\u002d\u2212"
PUNCT_UNICODE = "\u2019"
ADDS_UNICODE = "Ã©"
DAY_NUMERAL = pp.Word(pp.nums, exact=2)
YEAR = pp.Word(pp.nums, exact=4)
DATE_DDMMMYY = pp.Combine(DAY_NUMERAL + SHORT_MONTH + YEAR)
PHONE_NUMBER = pp.Word(pp.nums, min=4, as_keyword=True)
TIME = pp.Word(pp.nums, exact=4, as_keyword=True)
DUALTIME = pp.Combine(TIME + pp.Literal("/") + TIME)
DASH_DAY = pp.Word(DASH_UNICODE, exact=2)
NUMERICAL_DAY = pp.MatchFirst(
    [
        pp.Word(pp.nums, exact=2, as_keyword=True),
        pp.Word(pp.nums, exact=1, as_keyword=True),
    ]
)
CALENDAR_DAY = pp.MatchFirst([DASH_DAY, NUMERICAL_DAY])
CALENDAR_LINE = pp.Opt(pp.OneOrMore(CALENDAR_DAY), default=[])
CITY = pp.Word(pp.alphas, exact=3, as_keyword=True)


DURATION = pp.Combine(pp.Word(pp.nums, min=1) + "." + pp.Word(pp.nums, exact=2))
POSITIONS = pp.one_of("CA FO FB C RC", as_keyword=True)


def trim_name(s: str, loc: int, tokens: pp.ParseResults) -> str:
    value: str = tokens[1]
    return value.strip()


BUSINESS_PHONE = pp.original_text_for(pp.SkipTo(PHONE_NUMBER))
BUSINESS_PHONE.set_parse_action(trim_name)
BUSINESS_CALENDAR = pp.original_text_for(pp.SkipTo(CALENDAR_DAY))
BUSINESS_CALENDAR.set_parse_action(trim_name)
BUSINESS_NONE = pp.original_text_for(pp.SkipTo(pp.string_end))
BUSINESS_NONE.set_parse_action(trim_name)
BUSINESS_DURATION = pp.original_text_for(pp.SkipTo(DURATION))
BUSINESS_DURATION.set_parse_action(trim_name)


PageHeader2 = (
    pp.StringStart()
    + pp.SkipTo("CALENDAR", include=True)
    + DATE_MM_SLASH_DD("from_date")
    + pp.Word(DASH_UNICODE)
    + DATE_MM_SLASH_DD("to_date")
    + pp.StringEnd()
)
"""
Matches:
```
DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01
```
"""


BaseEquipment = (
    pp.StringStart()
    + CITY("base")
    + pp.Opt(CITY("satelite_base"))
    + pp.Word(pp.nums, exact=3)("equipment")
    + pp.StringEnd()
)
"""
Matches:
```
BOS 737
LAX SAN 737
```
"""


TripHeader = (
    pp.StringStart()
    + "SEQ"
    + pp.Word(pp.nums, min=1, as_keyword=True)("number")
    + pp.Word(pp.nums, min=1, as_keyword=True)("ops_count")
    + "OPS"
    + "POSN"
    + pp.OneOrMore(POSITIONS)("positions")
    + pp.Opt("ONLY")
    + pp.Opt(
        pp.ZeroOrMore(pp.Word(pp.printables, as_keyword=False), stop_on="OPERATION")
        + pp.Suppress("OPERATION"),
        default=list(),
    )("operations")
    + pp.Opt(
        pp.ZeroOrMore(pp.Word(pp.printables, as_keyword=True), stop_on="QUALIFICATION")
        + pp.Suppress("QUALIFICATION"),
        default=list(),
    )("qualifications")
    + pp.MatchFirst(
        [
            CALENDAR_HEADER,
            (
                pp.one_of(["Replaces", "New"])
                + "prior"
                + "month"
                + pp.Optional("deadhead")
            ),
        ]
    )
    + pp.StringEnd()
)
"""
Matches:
```
SEQ 25064   1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
SEQ 6292    1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU
SEQ 16945   1 OPS   POSN CA FO                SPECIAL QUALIFICATION                    MO TU WE TH FR SA SU
SEQ 25018   2 OPS   POSN CA FO                MEXICO QUALIFICATION                     MO TU WE TH FR SA SU
SEQ 30569   1 OPS   POSN CA FO                                                         New prior month
SEQ 30890   1 OPS   POSN CA FO                                                         Replaces prior month
SEQ 19448   1 OPS   POSN CA FO                ST. THOMAS OPERATION                     MO TU WE TH FR SA SU 
SEQ 265    10 OPS   POSN FB ONLY              GERMAN   OPERATION                       MO TU WE TH FR SA SU 
SEQ 264     4 OPS   POSN FB ONLY                                                       MO TU WE TH FR SA SU 
SEQ 657     2 OPS   POSN FO C                                                          MO TU WE TH FR SA SU 
SEQ 30097   1 OPS   POSN FB ONLY              JAPANESE OPERATION                       Replaces prior month 
```
"""


DutyPeriodReport = (
    pp.StringStart()
    + "RPT"
    + DUALTIME("report")
    + CALENDAR_LINE("calendar_entries")
    + pp.Opt(
        pp.Literal("sequence")
        + pp.Word(pp.nums, min=1)("sequence_number")
        + "/"
        + DATE_DDMMM("date")
    )
    + pp.Opt(pp.Literal("sequence") + DATE_DDMMM("date"))
    + pp.StringEnd()
)
"""
Matches:
```
                RPT 1237/1237                                                           2 −− −− −− −− −− −−
                RPT 1000/1000                                                          sequence 25384/30DEC
                RPT 1829/1829                                                          sequence 01JUL

```
"""


Flight = (
    pp.StringStart()
    + pp.Word(pp.nums, exact=1, as_keyword=True)("dutyperiod")
    + pp.Combine(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))(
        "day_of_sequence"
    )
    + pp.Word(pp.alphanums, exact=2, as_keyword=True)("equipment_code")
    + pp.Word(pp.nums)("flight_number")
    + CITY("departure_station")
    + DUALTIME("departure_time")
    + pp.Opt(pp.Word(pp.alphas, exact=1, as_keyword=True), default="")("crew_meal")
    + CITY("arrival_station")
    + DUALTIME("arrival_time")
    + DURATION("block")
    # FIXME synth time? Can this happen on a non deadhead?
    + pp.Opt(DURATION("ground"), default="0.00")
    + pp.Opt("X", default="")("equipment_change")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)
"""
Matches:
```
1  1/1 65 2131  SAN 1337/1337    ORD 1935/1735   3.58          1.10X                   −− −− −− −− −− −− −−


```
"""


FlightDeadhead = (
    pp.StringStart()
    + pp.Word(pp.nums, exact=1, as_keyword=True)("dutyperiod")
    + pp.Combine(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))(
        "day_of_sequence"
    )
    + pp.Word(pp.alphanums, exact=2, as_keyword=True)("equipment_code")
    + pp.Word(pp.nums)("flight_number")
    + pp.Literal("D")("deadhead")
    + pp.WordEnd()
    + CITY("departure_station")
    + DUALTIME("departure_time")
    + pp.Opt(pp.Word(pp.alphas, exact=1, as_keyword=True), default="")("crew_meal")
    + CITY("arrival_station")
    + DUALTIME("arrival_time")
    + pp.Word(pp.alphas, exact=2)("deadhead_block")
    + DURATION("synth")
    + pp.Opt(DURATION("ground"), default="0.00")
    + pp.Opt("X", default="")("equipment_change")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)
"""
Matches:
```
3  3/3 CE 2308D DFW 1635/1635    AUS 1741/1741    AA    1.06                                                
2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X
4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
```
"""


DutyPeriodRelease = (
    pp.StringStart()
    + "RLS"
    + DUALTIME("release_time")
    + DURATION("block")
    + DURATION("synth")
    + DURATION("total_pay")
    + DURATION("duty")
    + DURATION("flight_duty")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)
"""
Matches:
```
                                 RLS 0739/0439   4.49   0.00   4.49   6.19        5.49 −− −− −− −− −− −− −−
                                 RLS 2252/2252   0.00   5.46   5.46   6.46        0.00
```
"""


LayoverPhone = (
    pp.StringStart()
    + CITY("layover_city")
    + BUSINESS_PHONE("hotel")
    + PHONE_NUMBER("hotel_phone")
    + DURATION("rest")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)
LayoverNoPhone = (
    pp.StringStart()
    + CITY("layover_city")
    + pp.Opt(BUSINESS_DURATION("hotel"))
    + DURATION("rest")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)

Layover = pp.MatchFirst([LayoverPhone, LayoverNoPhone])
"""
```
Matches:
                MIA SONESTA MIAMI AIRPORT                   13054469000    11.27       −− −− −− −− −− −− −−
                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       −− −− −− −− −− −− −−
```
"""

HotelAdditionalPhone = (
    pp.StringStart()
    + pp.Literal("+")
    + CITY("layover_city")
    + pp.WordEnd()
    + BUSINESS_PHONE("hotel")
    + PHONE_NUMBER("hotel_phone")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)

HotelAdditionalNoPhone = (
    pp.StringStart()
    + pp.Literal("+")
    + CITY("layover_city")
    + pp.WordEnd()
    + BUSINESS_CALENDAR("hotel")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)
HotelAdditionalNone = (
    pp.StringStart()
    + pp.Literal("+")
    + CITY("layover_city")
    + pp.WordEnd()
    + BUSINESS_NONE("hotel")
    + pp.StringEnd()
)
HotelAdditional = pp.MatchFirst(
    [HotelAdditionalPhone, HotelAdditionalNoPhone, HotelAdditionalNone]
)
"""
Matches:
```
               +PHL MARRIOTT OLD CITY                       12152386000
               +PHL CAMBRIA HOTEL AND SUITES                12157325500
```
"""

TransportationPhone = (
    pp.StringStart()
    + pp.NotAny("+")
    + BUSINESS_PHONE("transportation")
    + PHONE_NUMBER("phone")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)
TransportationNoPhone = (
    pp.StringStart()
    + pp.NotAny("+")
    + BUSINESS_CALENDAR("transportation")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)
TransportationNone = (
    pp.StringStart() + pp.NotAny("+") + BUSINESS_NONE("transportation") + pp.StringEnd()
)
Transportation = pp.MatchFirst(
    [TransportationPhone, TransportationNoPhone, TransportationNone]
)
"""
Matches:
```
                    SIN FIN DE SERVICIOS                    3331223240
                    VIP TRANSPORTATION− OGG                 8088712702                 −− −− −−
                                                                                      −− −− −−
```
"""


TransportationAdditional = pp.MatchFirst(
    [TransportationPhone, TransportationNoPhone, TransportationNone]
)
"""
Matches:
```
                    SKY TRANSPORTATION SERVICE, LLC         8566169633
                    DESERT COACH                            6022866161                    
```
"""


TripFooter = (
    pp.StringStart()
    + "TTL"
    + DURATION("block")
    + DURATION("synth")
    + DURATION("total_pay")
    + DURATION("tafb")
    + CALENDAR_LINE("calendar_entries")
    + pp.StringEnd()
)
"""
Matches:
```
TTL                                              7.50   0.00   7.50        10.20       −− −− −−

```
"""


CalendarOnly = pp.StringStart() + CALENDAR_LINE("calendar_entries") + pp.StringEnd()
"""
Matches:
```
                                                                                       −− 17 18 19 20 21 22
                                                                                       23 24 25 26 27 28 29
```
"""


PageFooter = (
    pp.StringStart()
    + "COCKPIT"
    + "ISSUED"
    + DATE_DDMMMYY("issued")
    + "EFF"
    + DATE_DDMMMYY("effective")
    + CITY("base")
    + pp.Opt(CITY, default="")("satelite_base")
    + pp.Word(pp.nums, exact=3)("equipment")
    + (pp.Literal("INTL") | pp.Literal("DOM"))("division")
    + "PAGE"
    + pp.Word(pp.nums)("internal_page")
    + pp.StringEnd()
)
"""
Matches:
```
COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 737  DOM                              PAGE   644
COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 320  INTL                             PAGE  1178
```
"""
