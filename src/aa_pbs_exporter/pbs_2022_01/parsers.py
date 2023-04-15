# mypy: disable-error-code=override
import logging
from typing import Any

import pyparsing as pp

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException
from aa_pbs_exporter.snippets.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseResultProtocol,
)

# TODO use code from snippets
# TODO update snippets home

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

CALENDAR_HEADER = pp.Literal("MO") + "TU" + "WE" + "TH" + "FR" + "SA" + "SU"
MONTH_NUMERAL = pp.Word(pp.nums, exact=2)
DAY_NUMERAL = pp.Word(pp.nums, exact=2)
SHORT_MONTH = pp.Word(pp.alphas, exact=3)
DATE_DDMMM = MONTH_NUMERAL + SHORT_MONTH
DATE_MMSLASHDD = MONTH_NUMERAL + "/" + DAY_NUMERAL
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


class PageHeader1(IndexedStringParserProtocol):
    def __init__(self) -> None:
        self.success_state = "page_header_1"

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        if "DEPARTURE" in indexed_string.txt:
            parsed = raw.PageHeader1(source=indexed_string)
            # ctx.handle_parse_result(parsed)
            return ParseResult(self.success_state, parsed)
        raise ParseException("'DEPARTURE' not found in line.")


class PageHeader2(IndexedStringParserProtocol):
    def __init__(self) -> None:
        self.success_state = "page_header_2"
        self._parser = (
            pp.StringStart()
            + pp.SkipTo("CALENDAR", include=True)
            + DATE_MMSLASHDD("from_date")
            + pp.Word(DASH_UNICODE)
            + DATE_MMSLASHDD("to_date")
            + pp.StringEnd()
        )

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        print(result.as_dict())
        parsed = raw.PageHeader2(
            source=indexed_string,
            from_date="".join(result["from_date"]),  # type: ignore
            to_date="".join(result["to_date"]),  # type: ignore
        )
        return ParseResult(self.success_state, parsed)
        # try:
        #     if words[-2] == "CALENDAR":
        #         parsed = raw.PageHeader2(
        #             source=indexed_string, calendar_range=words[-1]
        #         )
        #         return ParseResult(self.success_state, parsed)
        #     raise ParseException(
        #         f"Found {words[-2]} instead of 'CALENDAR' in {indexed_string!r}."
        #     )
        # except KeyError as error:
        #     raise ParseException(
        #         f"unable to index position [-2] in  {indexed_string!r}"
        #     ) from error


class HeaderSeparator(IndexedStringParserProtocol):
    def __init__(self) -> None:
        self.success_state = "header_separator"

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        if "-" * 5 in indexed_string.txt or "\u2212" * 5 in indexed_string.txt:
            parsed = raw.HeaderSeparator(source=indexed_string)
            return ParseResult(self.success_state, parsed)
        raise ParseException("'-----' not found in line.")


class TripSeparator(IndexedStringParserProtocol):
    def __init__(self) -> None:
        self.success_state = "trip_separator"

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        if "-" * 5 in indexed_string.txt or "\u2212" * 5 in indexed_string.txt:
            parsed = raw.TripSeparator(source=indexed_string)
            return ParseResult(self.success_state, parsed)
        raise ParseException("'-----' not found in line.")


class BaseEquipment(IndexedStringParserProtocol):
    def __init__(self) -> None:
        self.success_state = "base_equipment"
        self._parser = (
            pp.StringStart()
            + pp.Word(pp.alphas, exact=3)("base")
            + pp.Opt(pp.Word(pp.alphas, exact=3)("satelite_base"))
            + pp.Word(pp.nums, exact=3)("equipment")
            + pp.StringEnd()
        )

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.BaseEquipment(
            source=indexed_string,
            base=result["base"],  # type: ignore
            satellite_base=result.get("satelite_base", ""),  # type: ignore
            equipment=result["equipment"],  # type: ignore
        )
        return ParseResult(self.success_state, parsed)


class TripHeader(IndexedStringParserProtocol):
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

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.TripHeader(
            source=indexed_string,
            number=result["number"],  # type: ignore
            ops_count=result["ops_count"],  # type: ignore
            positions=" ".join(result["positions"]),
            operations=" ".join(result["operations"]),
            special_qualification=" ".join(result["special_qualification"]),
            calendar="",
        )
        return ParseResult(self.success_state, parsed)


class DutyPeriodReport(IndexedStringParserProtocol):
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

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.DutyPeriodReport(
            source=indexed_string,
            report=result["report"],  # type: ignore
            calendar=" ".join(result["calendar_entries"]),
        )
        return ParseResult(self.success_state, parsed)


# 4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
# 2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X


class Flight(IndexedStringParserProtocol):
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
            # FIXME synth time? Can this happen on a non deadhead?
            + pp.Opt(DURATION("ground"), default="0.00")
            + pp.Opt("X", default="")("equipment_change")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.Flight(
            source=indexed_string,
            dutyperiod_idx=result["dutyperiod"],  # type: ignore
            dep_arr_day=result["day_of_sequence"],  # type: ignore
            eq_code=result["equipment_code"],  # type: ignore
            flight_number=result["flight_number"],  # type: ignore
            deadhead="",
            departure_station=result["departure_station"],  # type: ignore
            departure_time=result["departure_time"],  # type: ignore
            meal=result["crew_meal"],  # type: ignore
            arrival_station=result["arrival_station"],  # type: ignore
            arrival_time=result["arrival_time"],  # type: ignore
            block=result["block"],  # type: ignore
            synth="0.00",
            ground=result["ground"],  # type: ignore
            equipment_change=result["equipment_change"],  # type: ignore
            calendar=" ".join(result["calendar_entries"]),
        )
        return ParseResult(self.success_state, parsed)


# 4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
# 2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X
class FlightDeadhead(IndexedStringParserProtocol):
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

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.Flight(
            source=indexed_string,
            dutyperiod_idx=result["dutyperiod"],  # type: ignore
            dep_arr_day=result["day_of_sequence"],  # type: ignore
            eq_code=result["equipment_code"],  # type: ignore
            flight_number=result["flight_number"],  # type: ignore
            deadhead=result["deadhead"],  # type: ignore
            departure_station=result["departure_station"],  # type: ignore
            departure_time=result["departure_time"],  # type: ignore
            meal=result["crew_meal"],  # type: ignore
            arrival_station=result["arrival_station"],  # type: ignore
            arrival_time=result["arrival_time"],  # type: ignore
            block="0.00",
            synth=result["synth"],  # type: ignore
            ground=result["ground"],  # type: ignore
            equipment_change=result["equipment_change"],  # type: ignore
            calendar=" ".join(result["calendar_entries"]),
        )
        return ParseResult(self.success_state, parsed)


class DutyPeriodRelease(IndexedStringParserProtocol):
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

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.DutyPeriodRelease(
            source=indexed_string,
            release=result["release_time"],  # type: ignore
            block=result["block"],  # type: ignore
            synth=result["synth"],  # type: ignore
            total_pay=result["total_pay"],  # type: ignore
            duty=result["duty"],  # type: ignore
            flight_duty=result["flight_duty"],  # type: ignore
            calendar=" ".join(result["calendar_entries"]),
        )
        return ParseResult(self.success_state, parsed)


class Hotel(IndexedStringParserProtocol):
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
            + pp.Opt(PHONE_NUMBER, default="")("hotel_phone")
            + DURATION("rest")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.Hotel(
            source=indexed_string,
            layover_city=result["layover_city"],  # type: ignore
            name=result["hotel"],  # type: ignore
            phone=result["hotel_phone"],  # type: ignore
            rest=result["rest"],  # type: ignore
            calendar=" ".join(result["calendar_entries"]),
        )
        return ParseResult(self.success_state, parsed)


class HotelAdditional(IndexedStringParserProtocol):
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
            + pp.Opt(PHONE_NUMBER, default="")("hotel_phone")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.HotelAdditional(
            source=indexed_string,
            layover_city=result["layover_city"],  # type: ignore
            name=result["hotel"],  # type: ignore
            phone=result["hotel_phone"],  # type: ignore
            calendar="".join(result["calendar_entries"]),
        )
        return ParseResult(self.success_state, parsed)


class Transportation(IndexedStringParserProtocol):
    def __init__(self) -> None:
        self.success_state = "transportation"
        self._parser = (
            pp.StringStart()
            + pp.NotAny("+")
            + pp.original_text_for(
                pp.SkipTo(pp.Or([PHONE_NUMBER, CALENDAR_ENTRY, pp.StringEnd()]))
            )("transportation")
            + pp.Opt(~CALENDAR_ENTRY + PHONE_NUMBER, default="")("transportation_phone")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.Transportation(
            source=indexed_string,
            name=result.get("transportation", ""),  # type: ignore
            phone=" ".join(result["transportation_phone"]),
            calendar=" ".join(result["calendar_entries"]),
        )
        return ParseResult(self.success_state, parsed)


class TransportationAdditional(IndexedStringParserProtocol):
    def __init__(self) -> None:
        self.success_state = "transportation_additional"
        self._parser = (
            pp.StringStart()
            + pp.NotAny("+")
            + pp.original_text_for(
                pp.SkipTo(pp.Or([PHONE_NUMBER, CALENDAR_ENTRY, pp.StringEnd()]))
            )("transportation")
            + pp.Opt(~CALENDAR_ENTRY + PHONE_NUMBER, default="")("transportation_phone")
            + pp.ZeroOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        try:
            parsed = raw.TransportationAdditional(
                source=indexed_string,
                name=result["transportation"],  # type: ignore
                phone=" ".join(result["transportation_phone"]),
                calendar=" ".join(result["calendar_entries"]),
            )
        except KeyError as error:
            raise ParseException(
                f"Key missing in parsed {indexed_string!r}. Is there no transportation name? {str(error)}"
            ) from error
        return ParseResult(self.success_state, parsed)


class TripFooter(IndexedStringParserProtocol):
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

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:
            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.TripFooter(
            source=indexed_string,
            block=result["block"],  # type: ignore
            synth=result["synth"],  # type: ignore
            total_pay=result["total_pay"],  # type: ignore
            tafb=result["tafb"],  # type: ignore
            calendar=" ".join(result["calendar_entries"]),
        )
        return ParseResult(self.success_state, parsed)


class PageFooter(IndexedStringParserProtocol):
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

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        try:

            result = self._parser.parse_string(indexed_string.txt)
        except pp.ParseException as error:
            raise ParseException(f"{error}") from error
        parsed = raw.PageFooter(
            source=indexed_string,
            issued=result["issued"],  # type: ignore
            effective=result["effective"],  # type: ignore
            base=result["base"],  # type: ignore
            satelite_base=result["satelite_base"],  # type: ignore
            equipment=result["equipment"],  # type: ignore
            division=result["division"],  # type: ignore
            page=result["internal_page"],  # type: ignore
        )
        return ParseResult(self.success_state, parsed)


# def parse_file(file_path: Path, ctx: LineParseContext) -> raw.BidPackage:
#     scheme = ParseScheme()
#     skipper = make_skipper()
#     sp.parse_file(file_path=file_path, scheme=scheme, ctx=ctx, skipper=skipper)
#     return ctx.results_obj


# def parse_lines(lines: Iterable[str], ctx: LineParseContext) -> raw.BidPackage:
#     scheme = ParseScheme()
#     skipper = make_skipper()
#     sp.parse_lines(lines=lines, scheme=scheme, ctx=ctx, skipper=skipper)
#     return ctx.results_obj
