import logging
from typing import Callable, Dict, Sequence

import pyparsing as pp

from aa_pbs_exporter.models.raw_2022_10 import bid_package as raw
from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.util.parsing import state_parser as sp
from aa_pbs_exporter.util.parsing.indexed_string import IndexedString
from aa_pbs_exporter.util.parsing.parse_context import ParseContext
from aa_pbs_exporter.util.publisher_consumer import MessagePublisher
from aa_pbs_exporter.util.parsing.indexed_string_filter import (
    MultiTest,
    SkipTillMatch,
    SkipBlankLines,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

CALENDAR_HEADER = pp.Literal("MO") + "TU" + "WE" + "TH" + "FR" + "SA" + "SU"
MONTH_NUMERAL = pp.Word(pp.nums, exact=2)
SHORT_MONTH = pp.Word(pp.alphas, exact=3)
DATE_DDMMM = MONTH_NUMERAL + SHORT_MONTH
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
CALENDAR_ENTRY = pp.Or(
    [
        pp.Word(DASH_UNICODE, exact=2, as_keyword=True),
        pp.Word(pp.nums, exact=1, as_keyword=True),
        pp.Word(pp.nums, exact=2, as_keyword=True),
    ]
)
DURATION = pp.Combine(pp.Word(pp.nums, min=1) + "." + pp.Word(pp.nums, exact=2))


def data_starts(indexed_string: IndexedString) -> bool:

    if "DEPARTURE" in indexed_string.txt:
        return True
    return False


def make_skipper() -> Callable[[IndexedString], bool]:
    return MultiTest(testers=[SkipTillMatch(matcher=data_starts), SkipBlankLines()])


class LineParseContext(ParseContext):
    def __init__(self, source: str, messenger: MessagePublisher | None = None) -> None:
        if messenger is None:
            self.messenger = MessagePublisher(consumers=[])
        else:
            self.messenger = messenger
        self.source_name = source
        self.bid_package = raw.Package(source=source)

    def handle_parse_result(self, result):
        # print(f"In Handle with {data.__class__.__qualname__}")
        match result.__class__.__qualname__:
            case "PageHeader1":
                self.bid_package.pages.append(raw.Page(page_header_1=result))
            case "PageHeader2":
                self.bid_package.pages[-1].page_header_2 = result
            case "HeaderSeparator":
                pass
            case "BaseEquipment":
                self.bid_package.pages[-1].base_equipment = result
            case "TripHeader":
                self.bid_package.pages[-1].trips.append(raw.Trip(header=result))
            case "DutyPeriodReport":
                self.bid_package.pages[-1].trips[-1].dutyperiods.append(
                    raw.DutyPeriod(report=result)
                )
            case "Flight":
                self.bid_package.pages[-1].trips[-1].dutyperiods[-1].flights.append(
                    raw.Flight(flight=result)
                )
            case "DutyPeriodRelease":
                self.bid_package.pages[-1].trips[-1].dutyperiods[-1].release = result
            case "Hotel":
                layover = raw.Layover(hotel=result)
                self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover = layover
            case "HotelAdditional":
                self.bid_package.pages[-1].trips[-1].dutyperiods[
                    -1
                ].layover.hotel_additional = result
            case "Transportation":
                self.bid_package.pages[-1].trips[-1].dutyperiods[
                    -1
                ].layover.transportation = result
            case "TransportationAdditional":
                self.bid_package.pages[-1].trips[-1].dutyperiods[
                    -1
                ].layover.transportation_additional = result
            case "TripFooter":
                self.bid_package.pages[-1].trips[-1].footer = result
            case "TripSeparator":
                # could validate trip here
                pass
            case "PageFooter":
                # could validate page here
                self.bid_package.pages[-1].page_footer = result


class ParseScheme(sp.ParseScheme):
    def __init__(self) -> None:
        self.scheme: Dict[str, Sequence[sp.Parser]] = {
            "start": [PageHeader1()],
            "page_header_1": [PageHeader2()],
            "page_header_2": [HeaderSeparator()],
            "header_separator": [TripHeader(), BaseEquipment()],
            "base_equipment": [TripHeader()],
            "trip_header": [DutyPeriodReport()],
            "dutyperiod_report": [Flight(), FlightDeadhead()],
            "flight": [Flight(), FlightDeadhead(), DutyPeriodRelease()],
            "dutyperiod_release": [Hotel(), TripFooter()],
            "hotel": [Transportation(), DutyPeriodReport(), HotelAdditional()],
            "transportation": [DutyPeriodReport(), HotelAdditional()],
            "hotel_additional": [TransportationAdditional()],
            "transportation_additional": [DutyPeriodReport()],
            "trip_footer": [TripSeparator()],
            "trip_separator": [TripHeader(), PageFooter()],
            "page_footer": [PageHeader1()],
        }

    def expected(self, state: str) -> Sequence[sp.Parser]:
        return self.scheme[state]


class PageHeader1(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "page_header_1"

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        if "DEPARTURE" in indexed_string.txt:
            parsed = lines.PageHeader1(source=indexed_string)
            ctx.handle_parse_result(parsed)
            return self.success_state
        raise sp.ParseException("'DEPARTURE' not found in line.")


class PageHeader2(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "page_header_2"

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        words = indexed_string.txt.split()
        if words[-2] == "CALENDAR":
            parsed = lines.PageHeader2(source=indexed_string, calendar_range=words[-1])
            ctx.handle_parse_result(parsed)
            return self.success_state
        raise sp.ParseException(
            f"Found {words[-2]} instead of 'CALENDAR' in {indexed_string!r}."
        )


class HeaderSeparator(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "header_separator"

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        if "-" * 5 in indexed_string.txt or "\u2212" * 5 in indexed_string.txt:
            parsed = lines.HeaderSeparator(source=indexed_string)
            ctx.handle_parse_result(parsed)
            return self.success_state
        raise sp.ParseException("'-----' not found in line.")


class TripSeparator(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "trip_separator"

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        if "-" * 5 in indexed_string.txt or "\u2212" * 5 in indexed_string.txt:
            parsed = lines.TripSeparator(source=indexed_string)
            ctx.handle_parse_result(parsed)
            return self.success_state
        raise sp.ParseException("'-----' not found in line.")


class BaseEquipment(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "base_equipment"
        self._parser = (
            pp.StringStart()
            + pp.Word(pp.alphas, exact=3)("base")
            + pp.Opt(pp.Word(pp.alphas, exact=3)("satelite_base"))
            + pp.Word(pp.nums, exact=3)("equipment")
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.BaseEquipment(
            source=indexed_string,
            base=result["base"],
            satelite_base=result.get("satelite_base", ""),
            equipment=result["equipment"],
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class TripHeader(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "trip_header"
        # FIXME build progressive match, with options,
        # loop over list of possibles, take first match
        self._parser = (
            pp.StringStart()
            + "SEQ"
            + pp.Word(pp.nums, min=1, as_keyword=True)("number")
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
            + pp.Opt(pp.Literal("SPECIAL") + ("QUALIFICATION"), default="")(
                "special_qualification"
            )
            + pp.Or([CALENDAR_HEADER, (pp.Literal("Replaces") + "prior" + "month")])
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.TripHeader(
            source=indexed_string,
            number=result["number"],
            ops_count=result["ops_count"],
            positions=" ".join(result["positions"]),
            operations=" ".join(result["operations"]),
            special_qualification=" ".join(result["special_qualification"]),
            calendar="",
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class DutyPeriodReport(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "dutyperiod_report"
        self._parser = (
            pp.StringStart()
            + "RPT"
            + DUALTIME("report")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.Opt(
                pp.Literal("sequence")
                + pp.Word(pp.nums, min=1)("sequence_number")
                + "/"
                + DATE_DDMMM("date")
            )
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.DutyPeriodReport(
            source=indexed_string,
            report=result["report"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


# 4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
# 2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X


class Flight(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "flight"
        self._parser = (
            pp.StringStart()
            + pp.Word(pp.nums, exact=1, as_keyword=True)("dutyperiod")
            + pp.Combine(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))(
                "day_of_sequence"
            )
            + pp.Word(pp.nums, exact=2, as_keyword=True)("equipment_code")
            + pp.Word(pp.nums)("flight_number")
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("departure_station")
            + DUALTIME("departure_time")
            + pp.Opt(pp.Word(pp.alphas, exact=1, as_keyword=True), default="")(
                "crew_meal"
            )
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("arrival_station")
            + DUALTIME("arrival_time")
            + DURATION("block")
            # FIXME synth time?
            + pp.Opt(DURATION("ground"), default="0.00")
            + pp.Opt("X", default="")("equipment_change")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.Flight(
            source=indexed_string,
            dutyperiod_index=result["dutyperiod"],
            dep_arr_day=result["day_of_sequence"],
            eq_code=result["equipment_code"],
            flight_number=result["flight_number"],
            deadhead="",
            departure_station=result["departure_station"],
            departure_time=result["departure_time"],
            meal=result["crew_meal"],
            arrival_station=result["arrival_station"],
            arrival_time=result["arrival_time"],
            block=result["block"],
            synth="0.00",
            ground=result["ground"],
            equipment_change=result["equipment_change"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


# 4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
# 2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X
class FlightDeadhead(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "flight"
        self._parser = (
            pp.StringStart()
            + pp.Word(pp.nums, exact=1, as_keyword=True)("dutyperiod")
            + pp.Combine(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))(
                "day_of_sequence"
            )
            + pp.Word(pp.nums, exact=2, as_keyword=True)("equipment_code")
            + pp.Word(pp.nums)("flight_number")
            + pp.Literal("D")("deadhead")
            + pp.WordEnd()
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("departure_station")
            + DUALTIME("departure_time")
            + pp.Opt(pp.Word(pp.alphas, exact=1, as_keyword=True), default="")(
                "crew_meal"
            )
            + pp.Word(pp.alphas, exact=3, as_keyword=True)("arrival_station")
            + DUALTIME("arrival_time")
            + pp.Word(pp.alphas, exact=2)("deadhead_block")
            + DURATION("synth")
            + pp.Opt(DURATION("ground"), default="0.00")
            + pp.Opt("X", default="")("equipment_change")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.Flight(
            source=indexed_string,
            dutyperiod_index=result["dutyperiod"],
            dep_arr_day=result["day_of_sequence"],
            eq_code=result["equipment_code"],
            flight_number=result["flight_number"],
            deadhead=result["deadhead"],
            departure_station=result["departure_station"],
            departure_time=result["departure_time"],
            meal=result["crew_meal"],
            arrival_station=result["arrival_station"],
            arrival_time=result["arrival_time"],
            block="0.00",
            synth=result["synth"],
            ground=result["ground"],
            equipment_change=result["equipment_change"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class DutyPeriodRelease(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "dutyperiod_release"
        self._parser = (
            pp.StringStart()
            + "RLS"
            + DUALTIME("release_time")
            + DURATION("block")
            + DURATION("synth")
            + DURATION("total_pay")
            + DURATION("duty")
            + DURATION("flight_duty")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.DutyPeriodRelease(
            source=indexed_string,
            release=result["release_time"],
            block=result["block"],
            synth=result["synth"],
            total_pay=result["total_pay"],
            duty=result["duty"],
            flight_duty=result["flight_duty"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class Hotel(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "hotel"
        self._parser = (
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

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.Hotel(
            source=indexed_string,
            layover_city=result["layover_city"],
            name=result["hotel"],
            phone=result["hotel_phone"],
            rest=result["rest"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class HotelAdditional(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "hotel_additional"
        self._parser = (
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

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.HotelAdditional(
            source=indexed_string,
            layover_city=result["layover_city"],
            name=result["hotel"],
            phone=result["hotel_phone"],
            calendar="".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class Transportation(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "transportation"
        self._parser = (
            pp.StringStart()
            + pp.NotAny("+")
            + pp.original_text_for(
                pp.SkipTo(pp.Or([PHONE_NUMBER, CALENDAR_ENTRY, pp.StringEnd()]))
            )("transportation")
            + pp.Opt(~CALENDAR_ENTRY + PHONE_NUMBER, default=[])("transportation_phone")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.Transportation(
            source=indexed_string,
            name=result.get("transportation", ""),
            phone=" ".join(result["transportation_phone"]),
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class TransportationAdditional(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "transportation_additional"
        self._parser = (
            pp.StringStart()
            + pp.NotAny("+")
            + pp.original_text_for(
                pp.SkipTo(pp.Or([PHONE_NUMBER, CALENDAR_ENTRY, pp.StringEnd()]))
            )("transportation")
            + pp.Opt(~CALENDAR_ENTRY + PHONE_NUMBER, default=[])("transportation_phone")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.TransportationAdditional(
            source=indexed_string,
            name=result["transportation"],
            phone=" ".join(result["transportation_phone"]),
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class TripFooter(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "trip_footer"
        self._parser = (
            pp.StringStart()
            + "TTL"
            + DURATION("block")
            + DURATION("synth")
            + DURATION("total_pay")
            + DURATION("tafb")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.TripFooter(
            source=indexed_string,
            block=result["block"],
            synth=result["synth"],
            total_pay=result["total_pay"],
            tafb=result["tafb"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse_result(parsed)
        return self.success_state


class PageFooter(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "page_footer"
        self._parser = (
            pp.StringStart()
            + "COCKPIT"
            + "ISSUED"
            + DATE_DDMMMYY("issued")
            + "EFF"
            + DATE_DDMMMYY("effective")
            + pp.Word(pp.alphas, exact=3)("base")
            + pp.Opt(pp.Word(pp.alphas, exact=3)("satelite_base"), default="")
            + pp.Word(pp.nums, exact=3)("equipment")
            + (pp.Literal("INTL") | pp.Literal("DOM"))("division")
            + "PAGE"
            + pp.Word(pp.nums)("internal_page")
            + pp.StringEnd()
        )

    def parse(self, indexed_string: IndexedString, ctx: ParseContext) -> str:
        try:

            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = lines.PageFooter(
            source=indexed_string,
            issued=result["issued"],
            effective=result["effective"],
            base=result["base"],
            satelite_base=result["satelite_base"],
            equipment=result["equipment"],
            division=result["division"],
            page=result["internal_page"],
        )
        ctx.handle_parse_result(parsed)
        return self.success_state
