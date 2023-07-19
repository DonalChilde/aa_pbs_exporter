import logging
import re
from typing import Any

import pyparsing as pp

from aa_pbs_exporter.pbs_2022_01.models import raw_parsed as raw_p
from aa_pbs_exporter.pbs_2022_01.parser import grammar as g
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    SingleParserFail,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
    ParseResult,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class IndexedStringParser(IndexedStringParserProtocol):
    def __init__(self, success_state: str) -> None:
        super().__init__()
        self.success_state = success_state

    def parse(
        self, indexed_string: IndexedStringDict, ctx: dict[str, Any] | None, **kwargs
    ) -> ParseResult:
        raise NotImplementedError


class PyparsingParser(IndexedStringParser):
    p_parser: pp.ParserElement

    def get_result(self, indexed_string: IndexedStringDict) -> dict[str, Any]:
        try:
            result = self.p_parser.parse_string(indexed_string["txt"])
            result_dict = result.as_dict()
        except pp.ParseException as error:
            raise SingleParserFail(
                f"{error}",
                parser=self,
                indexed_string=indexed_string,
            ) from error
        return result_dict

    def parse(
        self, indexed_string: IndexedStringDict, ctx: dict[str, Any] | None, **kwargs
    ) -> ParseResult:
        raise NotImplementedError


class PageHeader1(IndexedStringParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        if "DEPARTURE" in indexed_string["txt"]:
            parsed_data: dict[str, Any] = {}
            return ParseResult(
                parse_ident=self.success_state,
                parsed_data=parsed_data,
                source=indexed_string,
            )
        raise SingleParserFail(
            f"'DEPARTURE' not found in {indexed_string!r}.",
            parser=self,
            indexed_string=indexed_string,
        )


class PageHeader2(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.PageHeader2

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.PageHeader2(
            from_date="".join(result_dict.get("from_date", "")),
            to_date="".join(result_dict.get("to_date", "")),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class HeaderSeparator(IndexedStringParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        if "-" * 5 in indexed_string["txt"] or "\u2212" * 5 in indexed_string["txt"]:
            parsed_data = raw_p.HeaderSeparator()
            return ParseResult(
                parse_ident=self.success_state,
                parsed_data=parsed_data,
                source=indexed_string,
            )
        raise SingleParserFail(
            "'-----' not found in line.",
            parser=self,
            indexed_string=indexed_string,
        )


class TripSeparator(IndexedStringParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        if "-" * 5 in indexed_string["txt"] or "\u2212" * 5 in indexed_string["txt"]:
            parsed_data = raw_p.TripSeparator()
            return ParseResult(
                parse_ident=self.success_state,
                parsed_data=parsed_data,
                source=indexed_string,
            )
        raise SingleParserFail(
            "'-----' not found in line.",
            parser=self,
            indexed_string=indexed_string,
        )


class BaseEquipment(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.BaseEquipment

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)

        parsed_data = raw_p.BaseEquipment(
            base=result_dict.get("base", ""),
            satellite_base=result_dict.get("satelite_base", ""),
            equipment=result_dict.get("equipment", ""),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class TripHeader(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        # FIXME build progressive match, with options,
        # loop over list of possibles, take first match
        self.p_parser = g.TripHeader

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.TripHeader(
            number=result_dict.get("number", ""),
            ops_count=result_dict.get("ops_count", ""),
            positions=" ".join(result_dict.get("positions", "")),
            operations=" ".join(result_dict.get("operations", "")),
            qualifications=" ".join(result_dict.get("qualifications", "")),
            # calendar="",
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


# TODO is this parser neeed?
class PriorMonthDeadhead(IndexedStringParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        if "PRIOR" in indexed_string["txt"]:
            parsed_data = raw_p.PriorMonthDeadhead()
            return ParseResult(
                parse_ident=self.success_state,
                parsed_data=parsed_data,
                source=indexed_string,
            )
        raise SingleParserFail(
            "'PRIOR' not found in line.",
            parser=self,
            indexed_string=indexed_string,
        )


class DutyPeriodReport(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.DutyPeriodReport

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.DutyPeriodReport(
            report=result_dict.get("report", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        # parsed_data.calendar.extend(result_dict.get("calendar_entries", []))
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


# 4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
# 2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X


class Flight(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.Flight

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.Flight(
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
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


# 4  4/4 64 2578D MIA 1949/1649    SAN 2220/2220    AA    5.31
# 2  2/2 45 1614D MCI 1607/1407    DFW 1800/1600    AA    1.53   1.27X
class FlightDeadhead(PyparsingParser):
    def __init__(self) -> None:
        super().__init__("Flight")
        self.p_parser = g.FlightDeadhead

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.Flight(
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
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class DutyPeriodRelease(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.DutyPeriodRelease

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.DutyPeriodRelease(
            release=result_dict.get("release_time", ""),
            block=result_dict.get("block", ""),
            synth=result_dict.get("synth", ""),
            total_pay=result_dict.get("total_pay", ""),
            duty=result_dict.get("duty", ""),
            flight_duty=result_dict.get("flight_duty", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class Layover(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.Layover

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.Layover(
            layover_city=result_dict.get("layover_city", ""),
            name=result_dict.get("hotel", ""),
            phone=result_dict.get("hotel_phone", ""),
            rest=result_dict.get("rest", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class HotelAdditional(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.HotelAdditional

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.HotelAdditional(
            layover_city=result_dict.get("layover_city", ""),
            name=result_dict.get("hotel", ""),
            phone=result_dict.get("hotel_phone", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class Transportation(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.Transportation

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.Transportation(
            name=result_dict.get("transportation", ""),
            phone=result_dict.get("phone", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class TransportationAdditional(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.TransportationAdditional

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs

        result_dict = self.get_result(indexed_string=indexed_string)
        try:
            parsed_data = raw_p.TransportationAdditional(
                name=result_dict.get("transportation", ""),
                phone=result_dict.get("transportation_phone", ""),
                calendar=result_dict.get("calendar_entries", []),
            )
        except KeyError as error:
            raise SingleParserFail(
                f"Key missing in parsed_data {indexed_string!r}. Is there no transportation name? {str(error)}",
                parser=self,
                indexed_string=indexed_string,
            ) from error
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class TripFooter(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.TripFooter

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.TripFooter(
            block=result_dict.get("block", ""),
            synth=result_dict.get("synth", ""),
            total_pay=result_dict.get("total_pay", ""),
            tafb=result_dict.get("tafb", ""),
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


class CalendarOnly(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.CalendarOnly

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx
        expected_len = 20
        ws_len = len(get_leading_whitespace(indexed_string["txt"]))
        if ws_len < expected_len:
            raise SingleParserFail(
                f"Expected at least {expected_len} leading whitespace characters, got {ws_len}",
                parser=self,
                indexed_string=indexed_string,
            )
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.CalendarOnly(
            calendar=result_dict.get("calendar_entries", []),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )


def get_leading_whitespace(txt: str) -> str:
    # TODO move to snippet
    # https://stackoverflow.com/a/2268559/105844
    matched = re.match(r"\s*", txt)
    if matched is None:
        return ""
    return matched.group()


class PageFooter(PyparsingParser):
    def __init__(self) -> None:
        super().__init__(self.__class__.__name__)
        self.p_parser = g.PageFooter

    def parse(
        self,
        indexed_string: IndexedStringDict,
        ctx: dict[str, Any] | None = None,
        **kwargs,
    ) -> ParseResult:
        _ = ctx, kwargs
        result_dict = self.get_result(indexed_string=indexed_string)
        parsed_data = raw_p.PageFooter(
            issued=result_dict.get("issued", ""),
            effective=result_dict.get("effective", ""),
            base=result_dict.get("base", ""),
            satelite_base=result_dict.get("satelite_base", ""),
            equipment=result_dict.get("equipment", ""),
            division=result_dict.get("division", ""),
            page=result_dict.get("internal_page", ""),
        )
        return ParseResult(
            parse_ident=self.success_state,
            parsed_data=parsed_data,
            source=indexed_string,
        )
