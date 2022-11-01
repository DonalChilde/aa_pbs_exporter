from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.models.raw_2022_10.raw_bid_package import SourceText
from aa_pbs_exporter.util import state_parser as sp
import pyparsing as pp
import logging

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


class ParseContext:
    def __init__(self, file_name: str) -> None:
        self.bid_package = raw.Package(file_name=file_name, package_date=None)

    def handle_parse(self, data):
        pass


class PageHeader1(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "page_header_1"

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        if "DEPARTURE" in line:
            source = SourceText(line_number, line)
            parsed = raw.PageHeader1(source=source)
            ctx.handle_parse(parsed)
            return self.success_state
        raise sp.ParseException("'DEPARTURE' not found in line.")


class PageHeader2(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "page_header_2"

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        words = line.split()
        if words[-2] == "CALENDAR":
            source = SourceText(line_number, line)
            parsed = raw.PageHeader2(source=source, calendar_range=words[-1])
            ctx.handle_parse(parsed)
            return self.success_state
        raise sp.ParseException(f"Found {words[-2]} instead of 'CALENDAR' in line.")


class HeaderSeparator(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "header_separator"

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        if "-" * 5 in line or "\u2212" * 5 in line:
            source = SourceText(line_number, line)
            parsed = raw.HeaderSeparator(source=source)
            ctx.handle_parse(parsed)
            return self.success_state
        raise sp.ParseException("'-----' not found in line.")


class TripSeparator(sp.Parser):
    def __init__(self) -> None:
        self.success_state = "trip_separator"

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        if "-" * 5 in line or "\u2212" * 5 in line:
            source = SourceText(line_number, line)
            parsed = raw.TripSeparator(source=source)
            ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.BaseEquipment(
            source=source,
            base=result["base"],
            satelite_base=result.get("satelite_base", ""),
            equipment=result["equipment"],
        )
        ctx.handle_parse(parsed)
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
            + pp.Opt(pp.Literal("SPECIAL") + ("QUALIFICATION"))("special_qualification")
            + pp.Or([CALENDAR_HEADER, (pp.Literal("Replaces") + "prior" + "month")])
            + pp.StringEnd()
        )

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.TripHeader(
            source=source,
            number=result["number"],
            ops_count=result["ops_count"],
            positions=" ".join(result["positions"]),
            calendar="",
        )
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.DutyPeriodReport(
            source=source,
            report=result["report"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.Flight(
            source=source,
            dutyperiod_index=result["dutyperiod"],
            d_a=result["day_of_sequence"],
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
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.Flight(
            source=source,
            dutyperiod_index=result["dutyperiod"],
            d_a=result["day_of_sequence"],
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
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.DuytPeriodRelease(
            source=source,
            release=result["release_time"],
            block=result["block"],
            synth=result["synth"],
            total_pay=result["total_pay"],
            duty=result["duty"],
            flight_duty=result["flight_duty"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.Hotel(
            source=source,
            layover_city=result["layover_city"],
            name=result["hotel"],
            phone=result["hotel_phone"],
            rest=result["rest"],
            calendar=" ".join(result["calendar_entries"]),
        )
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.HotelAdditional(
            source=source,
            layover_city=result["layover_city"],
            name=result["hotel"],
            phone=result["hotel_phone"],
            calendar="".join(result["calendar_entries"]),
        )
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.Transportation(
            source=source,
            name=result["transportation"],
            phone=result["transportation_phone"],
            calendar=result["calendar_entries"],
        )
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.TransportationAdditional(
            source=source,
            name=result["transportation"],
            phone=result["transportation_phone"],
            calendar=result["calendar_entries"],
        )
        ctx.handle_parse(parsed)
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

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.TripFooter(
            source=source,
            block=result["block"],
            synth=result["synth"],
            total_pay=result["total_pay"],
            tafb=result["tafb"],
            calendar=result["calendar_entries"],
        )
        ctx.handle_parse(parsed)
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
            + pp.Opt(pp.Word(pp.alphas, exact=3)("satelite_base"))
            + pp.Word(pp.nums, exact=3)("equipment")
            + (pp.Literal("INTL") | pp.Literal("DOM"))("division")
            + "PAGE"
            + pp.Word(pp.nums)("internal_page")
            + pp.StringEnd()
        )

    def parse(self, line_number: int, line: str, ctx: ParseContext) -> str:
        try:
            source = SourceText(line_number, line)
            result = self._parser.parse_string(line)
        except pp.ParseException as error:
            raise sp.ParseException(f"{error}") from error
        parsed = raw.PageFooter(
            source=source,
            issued=result["block"],
            effective=result["effective"],
            base=result["base"],
            satelite_base=result["satelite_base"],
            equipment=result["equipment"],
            division=result["division"],
            page=result["internal_page"],
        )
        ctx.handle_parse(parsed)
        return self.success_state
