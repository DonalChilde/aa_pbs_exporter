from datetime import date, datetime, time, timedelta
from typing import Any, Tuple

import pyparsing as pp
from pfmsoft.text_chunk_parser import Chunk, ChunkParser, ParseContext


def short_string_to_date(s: str, loc: int, tocs: pp.ParseResults) -> date:
    _, _ = s, loc
    return datetime.strptime(tocs[0][0], "%m%b%Y").date()


def string_to_time(s: str, loc: int, tocs: pp.ParseResults) -> time:
    _, _ = s, loc
    return datetime.strptime(tocs[0], "%H%M").time()


def duration_to_timedelta(s: str, loc: int, tocs: pp.ParseResults) -> timedelta:
    _, _ = s, loc
    return timedelta(hours=int(tocs[0]["hours"]), minutes=int(tocs[0]["minutes"]))


def string_to_int(s: str, loc: int, tocs: pp.ParseResults) -> int:
    _, _ = s, loc
    return int(tocs[0])


DASH_UNICODE = "\u002d\u2212"
DASH = pp.Word(DASH_UNICODE)
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
SEQ_NUMBER = pp.Word(pp.nums, min=1)("sequence_number")
OPS = pp.Word(pp.nums, min=1)("ops").set_parse_action(string_to_int)
POSITIONS = pp.one_of("CA FO", as_keyword=True)
INTL_OPERATION = pp.Opt(pp.Word(pp.alphas)("international_operation") + "OPERATION")
CALENDAR_HEADER = pp.Literal("MO") + "TU" + "WE" + "TH" + "FR" + "SA" + "SU"
CALENDAR_ENTRY = pp.Or(
    [
        pp.Word(DASH_UNICODE, exact=2, as_keyword=True),
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
CREW_MEAL = pp.Word(pp.alphas, exact=1, as_keyword=True)
DURATION = pp.Combine(
    pp.Word(pp.nums, min=1)("hours") + "." + pp.Word(pp.nums, exact=2)("minutes")
).set_parse_action(duration_to_timedelta)
PHONE_NUMBER = pp.Combine(pp.Word(pp.nums, min=4, as_keyword=True))


class PyparsingChunkParser(ChunkParser):
    def __init__(self, new_state: str, parser: pp.ParserElement):
        self.parser = parser
        self.new_state = new_state

    def _define_parser(self) -> pp.ParserElement:
        raise NotImplementedError()

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Any]:
        """returns a tuple of (state,data)"""
        try:
            result = self.parser.parse_string(chunk.text)
        except pp.ParseException as exc:
            self.raise_parse_fail(str(exc), chunk, state, exc=exc)
        return (self.new_state, result.as_dict())


class FooterLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

    COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               PHL 787  INTL                             PAGE  1990

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="footer", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
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
        return definition


class FirstHeaderLine(PyparsingChunkParser):
    """
     _summary_

     _extended_summary_
     .. code-block::


    DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/

     Args:
         PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="first_header", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + pp.Word("\x0c")
            + "DAY"
            + pp.OneOrMore(DASH)
            + "DEPARTURE"
            + pp.OneOrMore(DASH)
            + "ARRIVAL"
            + pp.OneOrMore(DASH)
            + "GRND/"
            + "REST/"
            + pp.StringEnd()
        )
        return definition


class SecondHeaderLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

    DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="second_header", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
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
            + DASH
            + pp.Group(MONTH_DAY)("calendar_to")
            + pp.StringEnd()
        )
        return definition


class DashLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

    −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="dash_line", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = pp.StringStart() + pp.OneOrMore(DASH) + pp.StringEnd()
        return definition


class BaseEqLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

    PHL 787

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="base_eq", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = pp.StringStart() + BASE + EQUIPMENT + pp.StringEnd()
        return definition


class SequenceHeaderLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

    SEQ 1313   28 OPS   POSN CA FO                GREEK OPERATION                          MO TU WE TH FR SA SU

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="sequence_header", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + "SEQ"
            + SEQ_NUMBER
            + OPS
            + "OPS"
            + "POSN"
            + pp.OneOrMore(POSITIONS)("positions")
            + INTL_OPERATION
            + CALENDAR_HEADER
            + pp.StringEnd()
        )
        return definition


class ReportLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

                    RPT 0800/0800                                                          −− −− −− −− −−  7 −−
                    RPT 1545/1545                                                          −− −− −− −− −− −− −−
                    RPT 0652/0652

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="report", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + "RPT"
            + TIME("report_local")
            + "/"
            + TIME("report_home")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition


class FlightLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

    2  2/2 26 2112  DFW 0600/0700  B LAX 0725/1025   3.25          2.35X
    1  1/1 64  508  MBJ 1306/1406    DFW 1700/1800   3.54                                  −− −− −− −− −− −− −−

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="flight", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
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
            + pp.Opt(DURATION("ground"))
            + pp.Opt("X")("equipment_change")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition


class ReleaseLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

                                     RLS 0054/0054   6.05   0.00   6.05  10.18        9.48 −− −− −−
                                     RLS 2203/2203   3.00   0.49   3.49   7.38        7.08
                                     RLS 0825/0325   7.15   0.00   7.15   8.45        8.15 16 −− 18 −− −− −− −−

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="release", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
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
        return definition


class HotelLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

                    LHR HI HIGH STREET                          442073684023   23.50       −− −− 25 −− −− −− −−
                    ATH HOTEL INFO IN CCI/CREW PORTAL                          25.10       −− −− −− −− −− −− −−
                    BDL SHERATON SPRINGFIELD MONARCH PLACE HOTE 14137811010    21.02
                   +LAS THE WESTIN LAS VEGAS HOTEL              17028365900


    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="hotel", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + CITY_CODE("layover_city")
            + pp.original_text_for(
                pp.Opt(
                    pp.OneOrMore(
                        ~PHONE_NUMBER
                        + ~DURATION
                        + pp.Word(pp.printables, as_keyword=True)
                    ),
                    default=None,
                )
            )("hotel")
            + pp.Opt(~DURATION + PHONE_NUMBER, default=None)("hotel_phone")
            + DURATION("rest")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition


class AdditionalHotelLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

                   +LAS THE WESTIN LAS VEGAS HOTEL              17028365900


    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="additional_hotel", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + pp.Word("+")
            + CITY_CODE("layover_city")
            + pp.original_text_for(
                pp.Opt(
                    pp.OneOrMore(
                        ~PHONE_NUMBER + pp.Word(pp.printables, as_keyword=True)
                    ),
                    default=None,
                )
            )("hotel")
            + pp.Opt(PHONE_NUMBER, default=None)("hotel_phone")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition


class TransportationLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

                        COMET CAR HIRE (CCH) LTD                442088979984               −− −− −−
                        TRANS INFO IN CCI/CREW PORTAL                                      −− −−  1
                        SHUTTLE


    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="transportation", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + pp.original_text_for(
                pp.Opt(
                    pp.OneOrMore(~PHONE_NUMBER + pp.Word(pp.printables)),
                    default=None,
                )
            )("transportation")
            + pp.Opt(~CALENDAR_ENTRY + PHONE_NUMBER, default=None)(
                "transportation_phone"
            )
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition


class TotalLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

    TTL                                             15.47   0.37  16.24        57.26
    TTL                                              4.58   0.17   5.15         7.18       −− −− −−
    TTL                                              4.54   0.21   5.15         7.16       30 −−  1

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="total", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + "TTL"
            + DURATION("block")
            + DURATION("synth")
            + DURATION("total_pay")
            + DURATION("tafb")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition
