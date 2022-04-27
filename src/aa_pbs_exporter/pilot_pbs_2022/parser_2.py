import logging
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Sequence, Tuple

import pyparsing as pp
from pfmsoft.text_chunk_parser import Chunk, ChunkParser, ParseContext, ParseSchema

from aa_pbs_exporter.models import bid_package_pydantic_base as model

logger = logging.getLogger(__name__)

# TODO PUNCT constant

DASH_UNICODE = "\u002d\u2212"
PUNCT_UNICODE = "\u2019"
ADDS_UNICODE = "Ã©"
DASH = pp.Word(DASH_UNICODE)
DAY_NUMERAL = pp.Word(pp.nums, exact=2)
SHORT_MONTH = pp.Word(pp.alphas, exact=3)
MONTH_NUMERAL = pp.Word(pp.nums, exact=2)
YEAR = pp.Word(pp.nums, exact=4)
DATE_DDMMMYY = pp.Combine(DAY_NUMERAL + SHORT_MONTH + YEAR)
# TIME = pp.Combine(pp.Word(pp.nums, exact=2) + pp.Word(pp.nums, exact=2))
MONTH_DAY = MONTH_NUMERAL + "/" + DAY_NUMERAL
DATE_MMslashDD = pp.Combine(
    pp.Word(pp.nums, exact=2)("month") + "/" + pp.Word(pp.nums, exact=2)("day")
)
DATE_DDMMM = MONTH_NUMERAL + SHORT_MONTH
# BASE = pp.Word(pp.alphas, exact=3)
# EQUIPMENT = pp.Word(pp.nums, exact=3)
# DIVISION = pp.Literal("INTL") | pp.Literal("DOM")
# SEQ_NUMBER = pp.Word(pp.nums, min=1)
# OPS = pp.Word(pp.nums, min=1)
# POSITIONS = pp.one_of("CA FO", as_keyword=True)
# INTL_OPERATION = pp.Opt(pp.Word(pp.alphas)) + "OPERATION"
CALENDAR_HEADER = pp.Literal("MO") + "TU" + "WE" + "TH" + "FR" + "SA" + "SU"
CALENDAR_ENTRY = pp.Or(
    [
        pp.Word(DASH_UNICODE, exact=2, as_keyword=True),
        pp.Word(pp.nums, exact=1, as_keyword=True),
        pp.Word(pp.nums, exact=2, as_keyword=True),
    ]
)
# DUTY_PERIOD = pp.Word(pp.nums, exact=1)
# EQUIPMENT_CODE = pp.Word(pp.nums, exact=2, as_keyword=True)
# DAY_OF_SEQUENCE = pp.Group(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))
# FLIGHT_NUMBER = pp.Word(pp.nums)
# CITY_CODE = pp.Word(pp.alphas, exact=3, as_keyword=True)
# CREW_MEAL = pp.Word(pp.alphas, exact=1, as_keyword=True)
# DEADHEAD_BLOCK = pp.Literal("AA")
DURATION = pp.Combine(pp.Word(pp.nums, min=1) + "." + pp.Word(pp.nums, exact=2))
PHONE_NUMBER = pp.Word(pp.nums, min=4, as_keyword=True)  # was combine...


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
            + DATE_DDMMMYY("issued")
            + "EFF"
            + DATE_DDMMMYY("effective")
            + pp.Word(pp.alphas, exact=3)("base")
            + pp.Opt(pp.Word(pp.alphas, exact=3)("satelite_base"))
            + pp.Word(pp.nums, exact=3)("equipment")
            + (pp.Literal("INTL") | pp.Literal("DOM"))("division")
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
            + DATE_MMslashDD("calendar_from")
            + DASH
            + DATE_MMslashDD("calendar_to")
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


class BaseEquipmentLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

    PHL 787

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="base_equipment", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + pp.Word(pp.alphas, exact=3)("base")
            + pp.Opt(pp.Word(pp.alphas, exact=3)("satelite_base"))
            + pp.Word(pp.nums, exact=3)("equipment")
            + pp.StringEnd()
        )
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
            + pp.Word(pp.nums, min=1, as_keyword=True)("sequence")
            + pp.Word(pp.nums, min=1, as_keyword=True)("ops_count")
            + "OPS"
            + "POSN"
            + pp.OneOrMore(pp.Word(pp.alphas, exact=2, as_keyword=True), stop_on="MO")(
                "positions"
            )
            + pp.Opt("ONLY")
            + pp.Opt(
                pp.ZeroOrMore(pp.Word(pp.alphas, as_keyword=True), stop_on="OPERATION")
                + pp.Suppress("OPERATION"),
                default=list(),
            )("operations")
            + pp.Opt(pp.Literal("SPECIAL") + ("QUALIFICATION"))("special_qualification")
            + pp.Or([CALENDAR_HEADER, (pp.Literal("Replaces") + "prior" + "month")])
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
        # TODO add support for replaces prior month sequence
        definition = (
            pp.StringStart()
            + "RPT"
            + pp.Word(pp.nums, exact=4, as_keyword=True)("report_local")
            + "/"
            + pp.Word(pp.nums, exact=4, as_keyword=True)("report_hbt")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.Opt(
                pp.Literal("sequence")
                + pp.Word(pp.nums, min=1)("sequence_number")
                + "/"
                + DATE_DDMMM("date")
            )
            + pp.StringEnd()
        )
        return definition


# FIXME flight.dutyperiod field


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
            + pp.Word(pp.nums, exact=1, as_keyword=True)("dutyperiod")
            + pp.Combine(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))(
                "day_of_sequence"
            )
            + pp.Word(pp.nums, exact=2, as_keyword=True)("equipment_code")
            + pp.Word(pp.nums)("flight_number")
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("departure_city")
            + pp.Word(pp.nums, exact=4, as_keyword=True)("departure_local")
            + "/"
            + pp.Word(pp.nums, exact=4, as_keyword=True)("departure_hbt")
            + pp.Opt(pp.Word(pp.alphas, exact=1, as_keyword=True), default="")(
                "crew_meal"
            )
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("arrival_city")
            + pp.Word(pp.nums, exact=4, as_keyword=True)("arrival_local")
            + "/"
            + pp.Word(pp.nums, exact=4, as_keyword=True)("arrival_hbt")
            + DURATION("block")
            + pp.Opt(DURATION("ground"), default="0.00")
            + pp.Opt("X")("equipment_change")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition


class FlightDeadheadLine(PyparsingChunkParser):
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
        super().__init__(new_state="flight_deadhead", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + pp.Word(pp.nums, exact=1, as_keyword=True)("dutyperiod")
            + pp.Combine(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))(
                "day_of_sequence"
            )
            + pp.Word(pp.nums, exact=2, as_keyword=True)("equipment_code")
            + pp.Word(pp.nums)("flight_number")
            + pp.original_text_for(pp.Word("D") + pp.WordEnd())("deadhead")
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("departure_city")
            + pp.Word(pp.nums, exact=4, as_keyword=True)("departure_local")
            + "/"
            + pp.Word(pp.nums, exact=4, as_keyword=True)("departure_hbt")
            + pp.Opt(pp.Word(pp.alphas, exact=1, as_keyword=True), default="")(
                "crew_meal"
            )
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("arrival_city")
            + pp.Word(pp.nums, exact=4, as_keyword=True)("arrival_local")
            + "/"
            + pp.Word(pp.nums, exact=4, as_keyword=True)("arrival_hbt")
            + pp.Word(pp.alphas, exact=2)("deadhead_block")
            + DURATION("synth")
            + pp.Opt(DURATION("ground"), default="0.00")
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
            + pp.Word(pp.nums, exact=4, as_keyword=True)("release_local")
            + "/"
            + pp.Word(pp.nums, exact=4, as_keyword=True)("release_hbt")
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

    # TODO spread this htel match over the other randomw word parsers.
    # TODO this could be XXX + skipto phone number or duration
    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("layover_city")
            + pp.original_text_for(
                pp.OneOrMore(
                    pp.Word(
                        pp.printables + PUNCT_UNICODE + DASH_UNICODE + ADDS_UNICODE
                    ),
                    stop_on=PHONE_NUMBER | DURATION,
                )
            )("hotel")
            + pp.Opt(PHONE_NUMBER, default=[])("hotel_phone")
            + DURATION("rest")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition


class HotelTestLine(PyparsingChunkParser):
    """
    _summary_

    _extended_summary_
    .. code-block::

                    LHR HI HIGH STREET                          442073684023   23.50       −− −− 25 −− −− −− −−
                    ATH HOTEL INFO IN CCI/CREW PORTAL                          25.10       −− −− −− −− −− −− −−
                    BDL SHERATON SPRINGFIELD MONARCH PLACE HOTE 14137811010    21.02
                   +LAS THE WESTIN LAS VEGAS HOTEL              17028365900
                    LIMOTOUR MONTRÃ©AL                      5148758715\n

    Args:
        PyparsingChunkParser: _description_
    """

    def __init__(self):
        super().__init__(new_state="hotel", parser=self._define_parser())

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("layover_city")
            + pp.original_text_for(
                pp.OneOrMore(
                    pp.CharsNotIn(" "),
                    stop_on=PHONE_NUMBER | DURATION,
                )
            )("hotel")
            + pp.Opt(PHONE_NUMBER, default=None)("hotel_phone")
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
            + pp.Literal("+")
            + pp.Word(pp.alphas, exact=3)("layover_city")
            + pp.WordEnd()
            + pp.original_text_for(
                pp.OneOrMore(
                    pp.Word(
                        pp.printables + PUNCT_UNICODE + DASH_UNICODE + ADDS_UNICODE
                    ),
                    stop_on=PHONE_NUMBER | DURATION,
                )
            )("hotel")
            + pp.Opt(PHONE_NUMBER, default=[])("hotel_phone")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        # TODO why does this phone number match as a string, and regular hotel as a list?
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
            + pp.NotAny("+")
            # + pp.original_text_for(
            #     pp.Opt(
            #         pp.OneOrMore(
            #             ~PHONE_NUMBER
            #             + pp.Word(ADDS_UNICODE +DASH_UNICODE+ PUNCT_UNICODE + pp.printables)
            #         ),
            #         default=None,
            #     )
            # )("transportation")
            + pp.original_text_for(
                pp.SkipTo(pp.Or([PHONE_NUMBER, CALENDAR_ENTRY, pp.StringEnd()]))
            )("transportation")
            + pp.Opt(~CALENDAR_ENTRY + PHONE_NUMBER, default=[])("transportation_phone")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )
        return definition


class AdditionalTransportationLine(PyparsingChunkParser):
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
        super().__init__(
            new_state="additional_transportation", parser=self._define_parser()
        )

    def _define_parser(self) -> pp.ParserElement:
        definition = (
            pp.StringStart()
            + pp.NotAny("+")
            + pp.original_text_for(pp.SkipTo(pp.Or([PHONE_NUMBER, pp.StringEnd()])))(
                "transportation"
            )
            + pp.Opt(PHONE_NUMBER, default=[])("transportation_phone")
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


class SkipChunk(ChunkParser):
    def __init__(self) -> None:
        pass

    def parse(
        self,
        chunk: Chunk,
        state: str,
        context: ParseContext,
    ) -> Tuple[str, Dict]:

        return (state, {})


class PbsSchema(ParseSchema):
    def __init__(self) -> None:
        self.schema = self._define_schema()

    def _define_schema(self) -> Dict[str, Sequence[ChunkParser]]:
        schema: Dict[str, Sequence[ChunkParser]] = {
            "origin": [FirstHeaderLine(), SkipChunk()],
            "first_header": [SecondHeaderLine()],
            "second_header": [DashLine()],
            "dash_line": [SequenceHeaderLine(), FooterLine(), BaseEquipmentLine()],
            "base_equipment": [SequenceHeaderLine()],
            "sequence_header": [ReportLine()],
            "report": [FlightLine(), FlightDeadheadLine()],
            "flight_deadhead": [FlightLine(), FlightDeadheadLine(), ReleaseLine()],
            "flight": [FlightLine(), FlightDeadheadLine(), ReleaseLine()],
            "release": [HotelLine(), TotalLine()],
            "hotel": [TransportationLine(), ReportLine(), AdditionalHotelLine()],
            "transportation": [ReportLine(), AdditionalHotelLine()],
            "additional_hotel": [AdditionalTransportationLine(), ReportLine()],
            "additional_transportation": [ReportLine()],
            "total": [DashLine()],
            "footer": [FirstHeaderLine()],
        }
        return schema

    def expected(self, state: str) -> Sequence[ChunkParser]:
        return self.schema[state]


def duration_dot_to_timedelta(duration: str) -> timedelta:
    hours, minutes = duration.split(".")
    return timedelta(hours=int(hours), minutes=int(minutes))


def hhmm_to_time(time_string: str) -> time:
    assert len(time_string) == 4
    hours = int(time_string[:2])
    minutes = int(time_string[-2:])
    return time(hour=hours, minute=minutes)


def mmdd_to_date(mmdd: Dict[str, str], year: int) -> date:
    month = int(mmdd["month"])
    day = int(mmdd["day"])
    return date(year, month, day)


class ContextParseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        # FIXME expand on this


class PbsContext(ParseContext):
    def __init__(self, year: int) -> None:
        self.year = year
        self.package: model.BidPackage | None = None
        self.current_page_sequences: List[model.BidSequence] = []
        self.header_count = 0
        self.calendar_entries: List[str] = []

    def second_header(self, data: Dict[str, Any], chunk: Chunk):
        if self.package is None:
            self.package = model.BidPackage(
                date_from=mmdd_to_date(data["calendar_from"], self.year),
                date_to=mmdd_to_date(data["calendar_to"], self.year),
                source=chunk.source,
            )

    def base_equipment(self, data):
        self.package.base.add(data["base"])
        if sat_base := data.get("satelite_base", None):
            self.package.satelite_bases.add(sat_base)
        self.package.equipment.add(data["equipment"])

    def sequence_header(self, data, chunk: Chunk):
        bid_sequence = model.BidSequence(
            three_part=None,
            sequence_number=data["sequence"],
            ops_count=int(data["ops_count"]),
            total_block=timedelta(),
            synth=timedelta(),
            total_pay=timedelta(),
            tafb=timedelta(),
            internal_page=0,
            from_line=chunk.chunk_id,
            to_line=0,
            positions=set(data["positions"]),
            operations=set(data["operations"]),
            special_qualification=bool(data.get("special_qualification", False)),
        )
        self.current_page_sequences.append(bid_sequence)
        self.header_count += 1

    def report(self, data):
        duty_period = model.DutyPeriod(
            report_local=hhmm_to_time(data["report_local"]),
            report_hbt=hhmm_to_time(data["report_hbt"]),
            release_local=time(hour=0, minute=0, second=30),
            release_hbt=time(hour=0, minute=0, second=30),
            block=timedelta(),
            synth=timedelta(),
            total_pay=timedelta(),
            duty=timedelta(),
            flight_duty=timedelta(),
            rest=timedelta(),
        )
        self.calendar_entries.extend(data["calendar_entries"])
        self.current_page_sequences[-1].duty_periods.append(duty_period)

    def flight(self, data):

        flight = model.Flight(
            equipment_code=data["equipment_code"],
            day=data["day_of_sequence"],
            flight_number=data["flight_number"],
            deadhead=False,
            departure_station=data["departure_city"],
            departure_local=hhmm_to_time(data["departure_local"]),
            departure_hbt=hhmm_to_time(data["departure_hbt"]),
            crewmeal=data["crew_meal"],
            arrival_station=data["arrival_city"],
            arrival_local=hhmm_to_time(data["arrival_local"]),
            arrival_hbt=hhmm_to_time(data["arrival_hbt"]),
            block=duration_dot_to_timedelta(data["block"]),
            synth=timedelta(),
            ground=duration_dot_to_timedelta(data["ground"]),
            equipment_change=bool(data.get("equipment_change", False)),
        )
        self.calendar_entries.extend(data["calendar_entries"])
        self.current_page_sequences[-1].duty_periods[-1].flights.append(flight)

    def flight_deadhead(self, data):
        flight = model.Flight(
            equipment_code=data["equipment_code"],
            day=data["day_of_sequence"],
            flight_number=data["flight_number"],
            deadhead=True,
            departure_station=data["departure_city"],
            departure_local=hhmm_to_time(data["departure_local"]),
            departure_hbt=hhmm_to_time(data["departure_hbt"]),
            crewmeal=data["crew_meal"],
            arrival_station=data["arrival_city"],
            arrival_local=hhmm_to_time(data["arrival_local"]),
            arrival_hbt=hhmm_to_time(data["arrival_hbt"]),
            block=timedelta(),
            synth=duration_dot_to_timedelta(data["synth"]),
            ground=duration_dot_to_timedelta(data["ground"]),
            equipment_change=bool(data.get("equipment_change", False)),
        )
        self.calendar_entries.extend(data["calendar_entries"])
        self.current_page_sequences[-1].duty_periods[-1].flights.append(flight)

    def release(self, data):
        duty_period = self.current_page_sequences[-1].duty_periods[-1]
        duty_period.release_local = hhmm_to_time(data["release_local"])
        duty_period.release_hbt = hhmm_to_time(data["release_hbt"])
        duty_period.block = duration_dot_to_timedelta(data["block"])
        duty_period.synth = duration_dot_to_timedelta(data["synth"])
        duty_period.total_pay = duration_dot_to_timedelta(data["total_pay"])
        duty_period.duty = duration_dot_to_timedelta(data["duty"])
        duty_period.flight_duty = duration_dot_to_timedelta(data["flight_duty"])
        self.calendar_entries.extend(data["calendar_entries"])

    def hotel(self, data):
        duty_period = self.current_page_sequences[-1].duty_periods[-1]
        hotel = model.Hotel(name=data["hotel"], phone="".join(data["hotel_phone"]))
        duty_period.rest = duration_dot_to_timedelta(data["rest"])
        duty_period.hotels.append(hotel)
        self.calendar_entries.extend(data["calendar_entries"])

    def transportation(self, data):
        duty_period = self.current_page_sequences[-1].duty_periods[-1]
        hotel = duty_period.hotels[-1]
        hotel.transportation = model.Transportation(
            name=data.get("transportation", ""),
            phone="".join(data["transportation_phone"]),
        )
        self.calendar_entries.extend(data["calendar_entries"])

    def additional_hotel(self, data):
        duty_period = self.current_page_sequences[-1].duty_periods[-1]
        hotel = model.Hotel(name=data["hotel"], phone="".join(data["hotel_phone"]))
        duty_period.hotels.append(hotel)
        self.calendar_entries.extend(data["calendar_entries"])

    def additional_transportation(self, data):
        duty_period = self.current_page_sequences[-1].duty_periods[-1]
        hotel = duty_period.hotels[-1]
        hotel.transportation = model.Transportation(
            name=data.get("transportation", ""),
            phone="".join(data["transportation_phone"]),
        )
        self.calendar_entries.extend(data["calendar_entries"])

    def total(self, data, chunk: Chunk):
        bid_sequence = self.current_page_sequences[-1]
        bid_sequence.total_block = duration_dot_to_timedelta(data["block"])
        bid_sequence.synth = duration_dot_to_timedelta(data["synth"])
        bid_sequence.total_pay = duration_dot_to_timedelta(data["total_pay"])
        bid_sequence.tafb = duration_dot_to_timedelta(data["tafb"])
        bid_sequence.to_line = int(chunk.chunk_id)
        self.calendar_entries.extend(data["calendar_entries"])
        self.collect_start_dates(
            bid_sequence=bid_sequence,
            calendar_entries=self.calendar_entries,
            start=self.package.date_from,  # type: ignore
            end=self.package.date_to,  # type: ignore
        )

    def footer(self, data):
        for bid_sequence in self.current_page_sequences:
            bid_sequence.three_part = model.ThreePartStatus(
                base=data["base"],
                equipment=data["equipment"],
                division=data["division"],
            )
            bid_sequence.internal_page = int(data["internal_page"])
        self.package.bid_sequences.extend(self.current_page_sequences)
        # reset for next page of data
        self.current_page_sequences.clear()
        self.calendar_entries.clear()

    def collect_start_dates(
        self,
        bid_sequence: model.BidSequence,
        calendar_entries: List[str],
        start: date,
        end: date,
    ):
        pass

    def parsed_data(self, state: str, data: Any, chunk: Chunk, parser: "ChunkParser"):
        """Handle the parsed data."""
        try:
            match state:
                case "second_header":
                    self.second_header(data, chunk)
                case "base_equipment":
                    self.base_equipment(data)
                case "sequence_header":
                    self.sequence_header(data, chunk)
                case "report":
                    self.report(data)
                case "flight":
                    self.flight(data)
                case "flight_deadhead":
                    self.flight_deadhead(data)
                case "release":
                    self.release(data)
                case "hotel":
                    self.hotel(data)
                case "transportation":
                    self.transportation(data)
                case "additional_hotel":
                    self.additional_hotel(data)
                case "additional_transportation":
                    self.additional_transportation(data)
                case "total":
                    self.total(data, chunk)
                case "footer":
                    self.footer(data)

        except Exception as exc:
            raise ContextParseException(
                "a better message", state, data, chunk, parser
            ) from exc

    def initialize(self):
        """
        Do any work required to initialize the context.

        _extended_summary_
        """

        logger.info("Initialize context")

    def cleanup(self):
        """
        Do any work required to clean up after context

        """
        logger.info("Cleanup context")
