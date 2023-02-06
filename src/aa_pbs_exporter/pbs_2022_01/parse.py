# mypy: disable-error-code=override
import logging
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Sequence

import pyparsing as pp

# from aa_pbs_exporter.models.raw_2022_10 import bid_package as raw
# from aa_pbs_exporter.models.raw_2022_10 import lines as raw_lines
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.snippets.state_parser import state_parser_protocols as spp
from aa_pbs_exporter.snippets.state_parser.parse_exception import ParseException

# from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
from aa_pbs_exporter.snippets.string.indexed_string_filter import (
    MultiTest,
    SkipBlankLines,
    SkipTillMatch,
)
from aa_pbs_exporter.snippets.string.indexed_string_protocol import (
    IndexedStringProtocol,
)

# from aa_pbs_exporter.snippets.messages.publisher_consumer import (
#     MessageConsumerProtocol,
#     MessagePublisherMixin,
# )
# from aa_pbs_exporter.snippets.parsing import state_parser as sp


# from aa_pbs_exporter.snippets.parsing.parse_context import ParseContext

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


def data_starts(indexed_string: IndexedStringProtocol) -> bool:

    if "DEPARTURE" in indexed_string.txt:
        return True
    return False


def make_skipper() -> Callable[[IndexedStringProtocol], bool]:
    return MultiTest(testers=[SkipTillMatch(matcher=data_starts), SkipBlankLines()])


@dataclass
class ParseResult:
    current_state: str
    parsed_data: raw.ParsedIndexedString


class ParseScheme:
    def __init__(self) -> None:
        self.scheme: Dict[str, Sequence[spp.IndexedStringParser]] = {
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

    def expected_parsers(
        self, current_state: str, **kwargs
    ) -> Sequence[spp.IndexedStringParser]:
        return self.scheme[current_state]


class ResultHandler(spp.ResultHandler):
    def __init__(self, source: str) -> None:
        super().__init__()
        self.source = source
        self.bid_package = raw.BidPackage(source=source, pages=[])

    def handle_result(self, parse_result: spp.ParseResult, **kwargs):
        match parse_result.parsed_data.__class__.__qualname__:
            case "PageHeader1":
                assert isinstance(parse_result.parsed_data, raw.PageHeader1)
                self.bid_package.pages.append(
                    raw.Page(page_header_1=parse_result.parsed_data, trips=[])
                )
            case "PageHeader2":
                assert isinstance(parse_result.parsed_data, raw.PageHeader2)
                self.bid_package.pages[-1].page_header_2 = parse_result.parsed_data
            case "HeaderSeparator":
                pass
            case "BaseEquipment":
                assert isinstance(parse_result.parsed_data, raw.BaseEquipment)
                self.bid_package.pages[-1].base_equipment = parse_result.parsed_data
            case "TripHeader":
                assert isinstance(parse_result.parsed_data, raw.TripHeader)
                self.bid_package.pages[-1].trips.append(
                    raw.Trip(header=parse_result.parsed_data, dutyperiods=[])
                )
            case "DutyPeriodReport":
                assert isinstance(parse_result.parsed_data, raw.DutyPeriodReport)
                self.bid_package.pages[-1].trips[-1].dutyperiods.append(
                    raw.DutyPeriod(report=parse_result.parsed_data, flights=[])
                )
            case "Flight":
                assert isinstance(parse_result.parsed_data, raw.Flight)
                self.bid_package.pages[-1].trips[-1].dutyperiods[-1].flights.append(
                    parse_result.parsed_data
                )
            case "DutyPeriodRelease":
                assert isinstance(parse_result.parsed_data, raw.DutyPeriodRelease)
                self.bid_package.pages[-1].trips[-1].dutyperiods[
                    -1
                ].release = parse_result.parsed_data
            case "Hotel":
                assert isinstance(parse_result.parsed_data, raw.Hotel)
                layover = raw.Layover(hotel=parse_result.parsed_data)
                self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover = layover
            case "HotelAdditional":
                assert isinstance(parse_result.parsed_data, raw.HotelAdditional)
                assert (
                    self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                    is not None
                )
                layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover

                layover.hotel_additional = parse_result.parsed_data
            case "Transportation":
                assert isinstance(parse_result.parsed_data, raw.Transportation)
                assert (
                    self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                    is not None
                )
                layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                layover.transportation = parse_result.parsed_data
            case "TransportationAdditional":
                assert isinstance(
                    parse_result.parsed_data, raw.TransportationAdditional
                )
                assert (
                    self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                    is not None
                )
                layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                layover.transportation_additional = parse_result.parsed_data
            case "TripFooter":
                assert isinstance(parse_result.parsed_data, raw.TripFooter)
                self.bid_package.pages[-1].trips[-1].footer = parse_result.parsed_data
            case "TripSeparator":
                # could validate trip here
                pass
            case "PageFooter":
                assert isinstance(parse_result.parsed_data, raw.PageFooter)
                # could validate page here
                self.bid_package.pages[-1].page_footer = parse_result.parsed_data


class ParseManager(spp.ParseManager):
    def __init__(
        self,
        ctx: dict[str, Any],
        result_handler: ResultHandler,
        parse_scheme: ParseScheme,
    ) -> None:
        super().__init__()
        self.ctx = ctx
        self.result_handler = result_handler
        self.parse_scheme = parse_scheme

    def expected_parsers(
        self, current_state: str, **kwargs
    ) -> Sequence[spp.IndexedStringParser]:
        return self.parse_scheme.expected_parsers(current_state=current_state)

    def handle_result(self, parse_result: ParseResult, **kwargs):
        self.result_handler.handle_result(parse_result=parse_result, **kwargs)


class PageHeader1(spp.IndexedStringParser):
    def __init__(self) -> None:
        self.success_state = "page_header_1"

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        if "DEPARTURE" in indexed_string.txt:
            parsed = raw.PageHeader1(source=indexed_string)
            # ctx.handle_parse_result(parsed)
            return ParseResult(self.success_state, parsed)
        raise ParseException("'DEPARTURE' not found in line.")


class PageHeader2(spp.IndexedStringParser):
    def __init__(self) -> None:
        self.success_state = "page_header_2"

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        words = indexed_string.txt.split()
        try:
            if words[-2] == "CALENDAR":
                parsed = raw.PageHeader2(
                    source=indexed_string, calendar_range=words[-1]
                )
                return ParseResult(self.success_state, parsed)
            raise ParseException(
                f"Found {words[-2]} instead of 'CALENDAR' in {indexed_string!r}."
            )
        except IndexError as error:
            raise ParseException(
                f"unable to index position [-2] in  {indexed_string!r}"
            ) from error


class HeaderSeparator(spp.IndexedStringParser):
    def __init__(self) -> None:
        self.success_state = "header_separator"

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        if "-" * 5 in indexed_string.txt or "\u2212" * 5 in indexed_string.txt:
            parsed = raw.HeaderSeparator(source=indexed_string)
            return ParseResult(self.success_state, parsed)
        raise ParseException("'-----' not found in line.")


class TripSeparator(spp.IndexedStringParser):
    def __init__(self) -> None:
        self.success_state = "trip_separator"

    def parse(
        self,
        indexed_string: raw.IndexedString,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        if "-" * 5 in indexed_string.txt or "\u2212" * 5 in indexed_string.txt:
            parsed = raw.TripSeparator(source=indexed_string)
            return ParseResult(self.success_state, parsed)
        raise ParseException("'-----' not found in line.")


class BaseEquipment(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class TripHeader(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class DutyPeriodReport(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class Flight(spp.IndexedStringParser):
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
    ) -> ParseResult:
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
class FlightDeadhead(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class DutyPeriodRelease(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class Hotel(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class HotelAdditional(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class Transportation(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class TransportationAdditional(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class TripFooter(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


class PageFooter(spp.IndexedStringParser):
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
    ) -> ParseResult:
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


def parse_file(file_path: Path) -> raw.BidPackage:
    scheme = ParseScheme()
    result_handler = ResultHandler(source=str(file_path))
    skipper = make_skipper()
    manager = ParseManager(ctx={}, result_handler=result_handler, parse_scheme=scheme)
    with open(file_path, encoding="utf-8") as file:
        try:
            parse_indexed_strings(file, manager=manager, skipper=skipper)
        except ParseException as error:
            logger.error("%s Failed to parse %r", file_path, error)
            raise error
    return result_handler.bid_package


def parse_string_by_line(source: str, string_data: str) -> raw.BidPackage:
    scheme = ParseScheme()
    result_handler = ResultHandler(source=str(source))
    skipper = make_skipper()
    manager = ParseManager(ctx={}, result_handler=result_handler, parse_scheme=scheme)
    line_iter = StringIO(string_data)
    parse_indexed_strings(strings=line_iter, manager=manager, skipper=skipper)
    return result_handler.bid_package


def parse_indexed_strings(
    strings: Iterable[str],
    manager: spp.ParseManager,
    skipper: Callable[[IndexedStringProtocol], bool] | None = None,
):
    """
    Parse a string iterable.

    Args:
        strings: _description_
        manager: _description_
        skipper: _description_. Defaults to None.

    Raises:
        error: _description_
    """
    current_state = "start"
    for idx, txt in enumerate(strings):
        indexed_string = raw.IndexedString(idx=idx, txt=txt)
        if skipper is not None and not skipper(indexed_string):
            continue
        try:
            parse_result = parse_indexed_string(
                indexed_string=indexed_string,
                parsers=manager.expected_parsers(current_state),
                ctx=manager.ctx,
            )
            manager.handle_result(parse_result=parse_result)
            current_state = parse_result.current_state
        except ParseException as error:
            logger.error("%s", error)
            raise error


def parse_indexed_string(
    indexed_string: IndexedStringProtocol,
    parsers: Sequence[spp.IndexedStringParser],
    ctx: dict[str, Any],
) -> spp.ParseResult:
    for parser in parsers:
        try:
            parse_result = parser.parse(indexed_string=indexed_string, ctx=ctx)
            logger.info("\n\tPARSED %r->%r", parser.__class__.__name__, indexed_string)
            return parse_result
        except ParseException as error:
            logger.info(
                "\n\tFAILED %r->%r\n\t%r",
                parser.__class__.__name__,
                indexed_string,
                error,
            )
    raise ParseException(f"No parser found for {indexed_string!r}\nTried {parsers!r}")


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
