import logging
import re
from typing import Any

import pyparsing as pp

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.models.parse_result import ParseResult
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_exception import (
    SingleParserFail,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseResultProtocol,
)

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
POSITIONS = pp.one_of("CA FO FB C", as_keyword=True)


class IndexedStringParser(IndexedStringParserProtocol):
    def __init__(self, success_state: str) -> None:
        super().__init__()
        self.success_state = success_state

    def parse(
        self, indexed_string: raw.IndexedString, ctx: dict[str, Any] | None, **kwargs
    ) -> ParseResult:
        raise NotImplementedError


class PyparsingParser(IndexedStringParser):
    p_parser: pp.ParserElement

    def get_result(self, indexed_string: raw.IndexedString) -> dict:
        try:
            result = self.p_parser.parse_string(indexed_string.txt)
            result_dict = result.as_dict()
        except pp.ParseException as error:
            raise SingleParserFail(
                f"{error}",
                parser=self,
                indexed_string=indexed_string,
            ) from error
        return result_dict

    def parse(
        self, indexed_string: raw.IndexedString, ctx: dict[str, Any] | None, **kwargs
    ) -> ParseResult:
        raise NotImplementedError


class PageHeader1(IndexedStringParser):
    def __init__(self) -> None:
        super().__init__("page_header_1")

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        _ = ctx, kwargs
        if "DEPARTURE" in indexed_string.txt:
            parsed = raw.PageHeader1(source=indexed_string)
            # ctx.handle_parse_result(parsed)
            return ParseResult(current_state=self.success_state, parsed_data=parsed)
        raise SingleParserFail(
            f"'DEPARTURE' not found in {indexed_string!r}.",
            parser=self,
            indexed_string=indexed_string,
        )


class PageHeader2(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("page_header_2")
        self.p_parser = (
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.PageHeader2(
            source=indexed_string,
            from_date="".join(result_dict.get("from_date", "")),
            to_date="".join(result_dict.get("to_date", "")),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)
        # try:
        #     if words[-2] == "CALENDAR":
        #         parsed = raw.PageHeader2(
        #             source=indexed_string, calendar_range=words[-1]
        #         )
        #         return ParseResult(self.success_state, parsed)
        #     raise SingleParserFail(
        #         f"Found {words[-2]} instead of 'CALENDAR' in {indexed_string!r}."
        #     )
        # except KeyError as error:
        #     raise SingleParserFail(
        #         f"unable to index position [-2] in  {indexed_string!r}"
        #     ) from error


class HeaderSeparator(IndexedStringParser):
    def __init__(self) -> None:
        super().__init__("header_separator")

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        _ = ctx, kwargs
        if "-" * 5 in indexed_string.txt or "\u2212" * 5 in indexed_string.txt:
            parsed = raw.HeaderSeparator(source=indexed_string)
            return ParseResult(current_state=self.success_state, parsed_data=parsed)
        raise SingleParserFail(
            "'-----' not found in line.",
            parser=self,
            indexed_string=indexed_string,
        )


class TripSeparator(IndexedStringParser):
    def __init__(self) -> None:
        super().__init__("trip_separator")

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        if "-" * 5 in indexed_string.txt or "\u2212" * 5 in indexed_string.txt:
            parsed = raw.TripSeparator(source=indexed_string)
            return ParseResult(current_state=self.success_state, parsed_data=parsed)
        raise SingleParserFail(
            "'-----' not found in line.",
            parser=self,
            indexed_string=indexed_string,
        )


class BaseEquipment(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("base_equipment")
        self.p_parser = (
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
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.BaseEquipment(
            source=indexed_string,
            base=result_dict.get("base", ""),
            satellite_base=result_dict.get("satelite_base", ""),
            equipment=result_dict.get("equipment", ""),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class TripHeader(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("trip_header")
        # FIXME build progressive match, with options,
        # loop over list of possibles, take first match
        self.p_parser = (
            pp.StringStart()
            + "SEQ"
            + pp.Word(pp.nums, min=1, as_keyword=True)("number")
            + pp.Word(pp.nums, min=1, as_keyword=True)("ops_count")
            + "OPS"
            + "POSN"
            # + pp.OneOrMore(
            #     pp.Word(pp.alphas, min=1, max=2, as_keyword=True), stop_on="MO"
            # )("positions")
            + pp.OneOrMore(POSITIONS)("positions")
            + pp.Opt("ONLY")
            + pp.Opt(
                pp.ZeroOrMore(
                    pp.Word(pp.printables, as_keyword=False), stop_on="OPERATION"
                )
                + pp.Suppress("OPERATION"),
                default=list(),
            )("operations")
            + pp.Opt(
                pp.ZeroOrMore(
                    pp.Word(pp.printables, as_keyword=True), stop_on="QUALIFICATION"
                )
                + pp.Suppress("QUALIFICATION"),
                default=list(),
            )("qualifications")
            # + pp.Opt(pp.Literal("SPECIAL") + ("QUALIFICATION"), default="")(
            #     "special_qualification"
            # )
            + pp.Or(
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

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.TripHeader(
            source=indexed_string,
            number=result_dict.get("number", ""),
            ops_count=result_dict.get("ops_count", ""),
            positions=" ".join(result_dict.get("positions", "")),
            operations=" ".join(result_dict.get("operations", "")),
            qualifications=" ".join(result_dict.get("qualifications", "")),
            # calendar="",
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class DutyPeriodReport(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("dutyperiod_report")
        self.p_parser = (
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
            + pp.Opt(pp.Literal("sequence") + DATE_DDMMM("date"))
            + pp.StringEnd()
        )

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResultProtocol:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.DutyPeriodReport(
            source=indexed_string,
            report=result_dict.get("report", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        # parsed.calendar.extend(result_dict.get("calendar_entries", []))
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


# 4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
# 2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X


class Flight(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("flight")
        self.p_parser = (
            pp.StringStart()
            + pp.Word(pp.nums, exact=1, as_keyword=True)("dutyperiod")
            + pp.Combine(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))(
                "day_of_sequence"
            )
            + pp.Word(pp.alphanums, exact=2, as_keyword=True)("equipment_code")
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.Flight(
            source=indexed_string,
            dutyperiod_idx=result_dict.get("dutyperiod", ""),
            dep_arr_day=result_dict.get("day_of_sequence", ""),
            eq_code=result_dict.get("equipment_code", ""),
            flight_number=result_dict.get("flight_number", ""),
            deadhead="",
            departure_station=result_dict.get("departure_station", ""),
            departure_time=result_dict.get("departure_time", ""),
            meal=result_dict.get("crew_meal", ""),
            arrival_station=result_dict.get("arrival_station", ""),
            arrival_time=result_dict.get("arrival_time", ""),
            block=result_dict.get("block", ""),
            synth="0.00",
            ground=result_dict.get("ground", ""),
            equipment_change=result_dict.get("equipment_change", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


# 4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
# 2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X
class FlightDeadhead(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("flight")
        self.p_parser = (
            pp.StringStart()
            + pp.Word(pp.nums, exact=1, as_keyword=True)("dutyperiod")
            + pp.Combine(pp.Word(pp.nums, exact=1) + "/" + pp.Word(pp.nums, exact=1))(
                "day_of_sequence"
            )
            + pp.Word(pp.alphanums, exact=2, as_keyword=True)("equipment_code")
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.Flight(
            source=indexed_string,
            dutyperiod_idx=result_dict.get("dutyperiod", ""),
            dep_arr_day=result_dict.get("day_of_sequence", ""),
            eq_code=result_dict.get("equipment_code", ""),
            flight_number=result_dict.get("flight_number", ""),
            deadhead=result_dict.get("deadhead", ""),
            departure_station=result_dict.get("departure_station", ""),
            departure_time=result_dict.get("departure_time", ""),
            meal=result_dict.get("crew_meal", ""),
            arrival_station=result_dict.get("arrival_station", ""),
            arrival_time=result_dict.get("arrival_time", ""),
            block="0.00",
            synth=result_dict.get("synth", ""),
            ground=result_dict.get("ground", ""),
            equipment_change=result_dict.get("equipment_change", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class DutyPeriodRelease(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("dutyperiod_release")
        self.p_parser = (
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.DutyPeriodRelease(
            source=indexed_string,
            release=result_dict.get("release_time", ""),
            block=result_dict.get("block", ""),
            synth=result_dict.get("synth", ""),
            total_pay=result_dict.get("total_pay", ""),
            duty=result_dict.get("duty", ""),
            flight_duty=result_dict.get("flight_duty", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class Hotel(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("hotel")
        self.p_parser = (
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.Hotel(
            source=indexed_string,
            layover_city=result_dict.get("layover_city", ""),
            name=result_dict.get("hotel", ""),
            phone=result_dict.get("hotel_phone", ""),
            rest=result_dict.get("rest", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class HotelAdditional(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("hotel_additional")
        self.p_parser = (
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.HotelAdditional(
            source=indexed_string,
            layover_city=result_dict.get("layover_city", ""),
            name=result_dict.get("hotel", ""),
            phone=result_dict.get("hotel_phone", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class Transportation(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("transportation")
        self.p_parser = (
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.Transportation(
            source=indexed_string,
            name=result_dict.get("transportation", ""),
            phone=" ".join(result_dict.get("transportation_phone", "")),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class TransportationAdditional(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("transportation_additional")
        self.p_parser = (
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
        _ = ctx, kwargs

        result_dict = self.get_result(indexed_string=indexed_string)
        try:
            parsed = raw.TransportationAdditional(
                source=indexed_string,
                name=result_dict.get("transportation", ""),
                phone=" ".join(result_dict.get("transportation_phone", "")),
                calendar=result_dict.get("calendar_entries", []),
            )
        except KeyError as error:
            raise SingleParserFail(
                f"Key missing in parsed {indexed_string!r}. Is there no transportation name? {str(error)}",
                parser=self,
                indexed_string=indexed_string,
            ) from error
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class TripFooter(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("trip_footer")
        self.p_parser = (
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.TripFooter(
            source=indexed_string,
            block=result_dict.get("block", ""),
            synth=result_dict.get("synth", ""),
            total_pay=result_dict.get("total_pay", ""),
            tafb=result_dict.get("tafb", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


class CalendarOnly(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("calendar_only")
        self.p_parser = (
            pp.StringStart()
            + pp.OneOrMore(CALENDAR_ENTRY)("calendar_entries")
            + pp.StringEnd()
        )

    def parse(
        self, indexed_string: raw.IndexedString, ctx: dict[str, Any], **kwargs
    ) -> ParseResult:
        expected_len = 20
        ws_len = len(get_leading_whitespace(indexed_string.txt))
        if ws_len < expected_len:
            raise SingleParserFail(
                f"Expected at least {expected_len} leading whitespace characters, got {ws_len}",
                parser=self,
                indexed_string=indexed_string,
            )
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.CalendarOnly(
            source=indexed_string,
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)


def get_leading_whitespace(txt: str) -> str:
    # TODO move to snippet
    # https://stackoverflow.com/a/2268559/105844
    matched = re.match(r"\s*", txt)
    if matched is None:
        return ""
    return matched.group()


class PageFooter(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("page_footer")
        self.p_parser = (
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
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed = raw.PageFooter(
            source=indexed_string,
            issued=result_dict.get("issued", ""),
            effective=result_dict.get("effective", ""),
            base=result_dict.get("base", ""),
            satelite_base=result_dict.get("satelite_base", ""),
            equipment=result_dict.get("equipment", ""),
            division=result_dict.get("division", ""),
            page=result_dict.get("internal_page", ""),
        )
        return ParseResult(current_state=self.success_state, parsed_data=parsed)
