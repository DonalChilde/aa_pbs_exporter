# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, List, Set
from zoneinfo import ZoneInfo
from uuid import UUID, uuid5
import json
from aa_pbs_exporter import PROJECT_NAMESPACE

from aa_pbs_exporter.airports.airport_model import Airport
from aa_pbs_exporter.models.raw_2022_10 import lines
from aa_pbs_exporter.util.complete_partial_datetime import (
    complete_future_mdt,
    complete_future_time,
)
from aa_pbs_exporter.util.dataclass_repr_mixin import DataclassReprMixin
from aa_pbs_exporter.util.index_numeric_strings import index_numeric_strings
from aa_pbs_exporter.util.parsing.indexed_string import IndexedString
from aa_pbs_exporter.util.line_ref import LineReference
from aa_pbs_exporter.util.parse_duration_regex import (
    parse_duration as regex_parse_duration,
)
from aa_pbs_exporter.util.parse_duration_regex import pattern_HHHMM

DATE = "%d%b%Y"
TIME = "%H%M"
MONTH_DAY = "%m/%d"
DURATION_PATTERN = pattern_HHHMM(hm_sep=".")

# TODO consolidate validation functions, make reporting easier and more consistent
@dataclass
class ResolvedFlight(DataclassReprMixin):
    resolved_trip_start: datetime
    departure: datetime
    arrival: datetime


@dataclass
class ResolvedDutyperiod(DataclassReprMixin):
    resolved_trip_start: datetime
    report: datetime
    release: datetime


@dataclass
class LocalHbt(DataclassReprMixin):
    local: str
    hbt: str


@dataclass
class Flight(DataclassReprMixin):
    flight: lines.Flight
    resolved_flights: dict[datetime, ResolvedFlight] = field(default_factory=dict)
    cached_values: dict[str, Any] = field(default_factory=dict)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def dp_idx(self) -> str:
        return self.flight.dutyperiod_index

    def dep_arr_day(self) -> str:
        return self.flight.dep_arr_day

    def eq_code(self) -> str:
        return self.flight.eq_code

    def number(self) -> str:
        return self.flight.flight_number

    def deadhead(self) -> bool:
        return bool(self.flight.deadhead)

    def departure_station(self) -> str:
        return self.flight.departure_station.upper()

    def departure_time(self) -> LocalHbt:
        local, hbt = self.flight.departure_time.split("/")
        return LocalHbt(local, hbt)

    def resolved_departure_time(self, resolved_report: datetime) -> str:
        raise NotImplementedError

    def meal(self) -> str:
        return self.flight.meal.upper()

    def arrival_station(self) -> str:
        return self.flight.arrival_station.upper()

    def arrival_time(self) -> LocalHbt:
        local, hbt = self.flight.arrival_time.split("/")
        return LocalHbt(local, hbt)

    def block(self) -> timedelta:
        return self._cached_duration("block", self.flight.block)  # type: ignore

    def synth(self) -> timedelta:
        return self._cached_duration("synth", self.flight.synth)  # type: ignore

    def ground(self) -> timedelta:
        return self._cached_duration("ground", self.flight.ground)  # type: ignore

    def equipment_change(self) -> bool:
        return bool(self.equipment_change)

    def _cached_duration(self, key: str, raw_str: str) -> timedelta:
        cached_value = self.cached_values.get(key, None)
        if cached_value is None:
            cached_value = parse_duration(raw_str)  # type: ignore
            self.cached_values[key] = cached_value
        return cached_value


@dataclass
class Layover(DataclassReprMixin):
    hotel: lines.Hotel
    transportation: lines.Transportation | None = None
    hotel_additional: lines.HotelAdditional | None = None
    transportation_additional: lines.TransportationAdditional | None = None
    cached_values: dict[str, Any] = field(default_factory=dict)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def city(self) -> str:
        return self.hotel.layover_city

    def rest(self) -> timedelta:
        return self._cached_duration("rest", self.hotel.rest)  # type: ignore

    def hotel_name(self) -> str | None:
        if not self.hotel.name:
            return None
        return self.hotel.name

    def hotel_phone(self) -> str | None:
        if not self.hotel.phone:
            return None
        return self.hotel.phone

    def transportation_name(self) -> str | None:
        if self.transportation is None:
            return None
        if not self.transportation.name:
            return None
        return self.transportation.name

    def transportation_phone(self) -> str | None:
        if self.transportation is None:
            return None
        if not self.transportation.phone:
            return None
        return self.transportation.phone

    def hotel_additional_name(self) -> str | None:
        if self.hotel_additional is None:
            return None
        if not self.hotel_additional.name:
            return None
        return self.hotel_additional.name

    def hotel_additional_phone(self) -> str | None:
        if self.hotel_additional is None:
            return None
        if not self.hotel_additional.phone:
            return None
        return self.hotel_additional.phone

    def transportation_additional_name(self) -> str | None:
        if self.transportation_additional is None:
            return None
        if not self.transportation_additional.name:
            return None
        return self.transportation_additional.name

    def transportation_additional_phone(self) -> str | None:
        if self.transportation_additional is None:
            return None
        if not self.transportation_additional.phone:
            return None
        return self.transportation_additional.phone

    def _cached_duration(self, key: str, raw_str: str) -> timedelta:
        cached_value = self.cached_values.get(key, None)
        if cached_value is None:
            cached_value = parse_duration(raw_str)  # type: ignore
            self.cached_values[key] = cached_value
        return cached_value


@dataclass
class DutyPeriod(DataclassReprMixin):
    report: lines.DutyPeriodReport
    release: lines.DutyPeriodRelease | None = None
    layover: Layover | None = None
    flights: List[Flight] = field(default_factory=list)
    resolved_reports: dict[datetime, ResolvedDutyperiod] = field(default_factory=dict)
    cached_values: dict[str, Any] = field(default_factory=dict)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def report_time(self) -> LocalHbt:
        local, hbt = self.report.report.split("/")
        return LocalHbt(local, hbt)

    def report_station(self) -> str:
        return self.flights[0].departure_station()

    def release_time(self) -> LocalHbt:
        local, hbt = self.release.release.split("/")  # type: ignore
        return LocalHbt(local, hbt)

    def release_station(self) -> str:
        return self.flights[-1].arrival_station()

    def block(self) -> timedelta:
        return self._cached_duration("block", self.release.block)  # type: ignore

    def synth(self) -> timedelta:
        return self._cached_duration("synth", self.release.synth)  # type: ignore

    def pay(self) -> timedelta:
        return self._cached_duration("total_pay", self.release.total_pay)  # type: ignore

    def duty(self) -> timedelta:
        return self._cached_duration("duty", self.release.duty)  # type: ignore

    def flight_duty(self) -> timedelta:
        return self._cached_duration("flight_duty", self.release.flight_duty)  # type: ignore

    def _sum_flight_durations(self, resolved_start_date: datetime) -> timedelta:
        total = timedelta()
        for flight in self.flights:
            total = total + (
                flight.resolved_flights[resolved_start_date].arrival
                - flight.resolved_flights[resolved_start_date].departure
            )
            total = total + flight.ground()
        return total

    def _cached_duration(self, key: str, raw_str: str) -> timedelta:
        cached_value = self.cached_values.get(key, None)
        if cached_value is None:
            cached_value = parse_duration(raw_str)  # type: ignore
            self.cached_values[key] = cached_value
        return cached_value

    def _source_lines(self) -> list[IndexedString]:
        source_lines: list[IndexedString] = []
        source_lines.append(self.report.source)
        for flight in self.flights:
            source_lines.append(flight.flight.source)
        if self.release:
            source_lines.append(self.release.source)
        if self.layover:
            source_lines.append(self.layover.hotel.source)
            if value := self.layover.transportation:
                source_lines.append(value.source)
            if self.layover.hotel_additional:
                source_lines.append(self.layover.hotel_additional.source)
            if self.layover.transportation_additional:
                source_lines.append(self.layover.transportation_additional.source)
        return source_lines

    def resolve_flight_dates(
        self,
        resolved_start_date: datetime,
        resolved_report: datetime,
        airports: dict[str, Airport],
    ):
        """Resolve departure and arrival times for the start date."""
        depart_lcl = self.flights[0].departure_time().local
        tz_string = airports[self.flights[0].departure_station()].tz
        departure = complete_future_time(
            resolved_report, depart_lcl, tz_info=ZoneInfo(tz_string), strf=TIME
        )
        for flight in self.flights:
            depart_lcl = flight.departure_time().local
            if departure.strftime("%H%M") != depart_lcl:
                raise ValueError(
                    f"{departure.isoformat()} time does not "
                    f"match local departure {depart_lcl} {flight=}"
                )
            if flight.block() > timedelta():
                arrival = departure + flight.block()
            elif flight.synth() > timedelta():
                arrival = departure + flight.synth()
            else:
                raise ValueError(
                    f"{flight=} block and synth are 0, unable to compute arrival time."
                )
            tz_string = airports[flight.arrival_station()].tz
            arrival = arrival.astimezone(ZoneInfo(tz_string))
            arrival_lcl = flight.arrival_time().local
            if arrival.strftime("%H%M") != arrival_lcl:
                raise ValueError(
                    f"{arrival.isoformat()} time does not "
                    f"match local arrival {arrival_lcl} {flight=}"
                )
            flight.resolved_flights[resolved_start_date] = ResolvedFlight(
                resolved_trip_start=resolved_start_date,
                departure=departure,
                arrival=arrival,
            )
            ground = flight.ground()
            if ground > timedelta():
                departure = arrival + ground
            else:
                # This will cause an error if any but the last flight is
                # missing a ground time
                departure = None


@dataclass
class Trip(DataclassReprMixin):
    header: lines.TripHeader
    footer: lines.TripFooter | None = None
    dutyperiods: List[DutyPeriod] = field(default_factory=list)
    resolved_start_dates: list[datetime] = field(default_factory=list)
    cached_values: dict[str, Any] = field(default_factory=dict)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def uuid(self, resolved_start_date: datetime) -> UUID:
        cached_value = self.cached_values.get("hash_string", None)
        if cached_value is None:
            cached_value = (
                f"{json.dumps(asdict(self.header))}"
                f"{json.dumps(asdict(self.footer))}"
                # f"{json.dumps(list([asdict(x) for x in self.dutyperiods]))}"
            )
            self.cached_values["hash_string"] = cached_value
        value = f"{resolved_start_date.isoformat()}{cached_value}"
        return uuid5(PROJECT_NAMESPACE, value)

    def number(self) -> str:
        return self.header.number

    def ops_count(self) -> str:
        return self.header.ops_count

    def base(self, page: "Page") -> str:
        return page.base()  # type: ignore

    def satelite_base(self, page: "Page") -> str | None:
        return page.satelite_base()  # type: ignore

    def positions(self) -> str:
        return self.header.positions

    def operations(self) -> str | None:
        return self.header.operations

    def division(self, page: "Page") -> str:
        return page.page_footer.division  # type: ignore

    def equipment(self, page: "Page") -> str:
        return page.page_footer.equipment  # type: ignore

    def special_qualification(self) -> bool:
        return bool(self.header.special_qualification)

    def _cached_duration(self, key: str, raw_str: str) -> timedelta:
        cached_value = self.cached_values.get(key, None)
        if cached_value is None:
            cached_value = parse_duration(raw_str)  # type: ignore
            self.cached_values[key] = cached_value
        return cached_value

    def block(self) -> timedelta:
        return self._cached_duration("block", self.footer.block)  # type: ignore

    def synth(self) -> timedelta:
        return self._cached_duration("synth", self.footer.synth)  # type: ignore

    def pay(self) -> timedelta:
        return self._cached_duration("total_pay", self.footer.total_pay)  # type: ignore

    def tafb(self) -> timedelta:
        return self._cached_duration("tafb", self.footer.tafb)  # type: ignore

    def resolve_all_the_dates(
        self, from_date: datetime, to_date: datetime, airports: dict[str, Airport]
    ):
        """Resolve all the report, release, departure, and arrival dates for each start date."""
        start_dates = self._start_dates(from_date=from_date, to_date=to_date)
        self._resolve_start_dates(start_dates=start_dates, airports=airports)
        for start in self.resolved_start_dates:
            self._resolve_trip_dates(start, airports=airports)

    def _line_range(self) -> str:
        if self.footer:
            to_line = self.footer.source.idx
        else:
            to_line = "UNDEFINED"
        return f"{self.header.source.idx}-{to_line}"

    def _source_lines(self) -> list[IndexedString]:
        source_lines: list[IndexedString] = []
        source_lines.append(self.header.source)
        for dutyperiod in self.dutyperiods:
            # pylint: disable=protected-access
            source_lines.extend(dutyperiod._source_lines())
        if self.footer:
            source_lines.append(self.footer.source)
        return source_lines

    def _resolve_trip_dates(
        self, resolved_start_date: datetime, airports: dict[str, Airport]
    ):
        """Calculate resolved report, release, departure, and arrival.

        Complete calculations by adding up times as necessary.

        """
        first_report_time = parse_time(self.dutyperiods[0].report_time().local)
        report = resolved_start_date.replace(
            hour=first_report_time.tm_hour, minute=first_report_time.tm_min
        )
        for dutyperiod in self.dutyperiods:
            tz_string = airports[dutyperiod.release_station()].tz
            release = report + dutyperiod.duty()
            release = release.astimezone(ZoneInfo(tz_string))
            resolved = ResolvedDutyperiod(
                resolved_trip_start=resolved_start_date, report=report, release=release
            )
            dutyperiod.resolved_reports[resolved.resolved_trip_start] = resolved
            dutyperiod.resolve_flight_dates(
                resolved_start_date=resolved_start_date,
                resolved_report=report,
                airports=airports,
            )
            if dutyperiod.layover is not None:
                # This should make resolved_ref == the report of the next dp
                report = release + dutyperiod.layover.rest()
            else:
                # This will cause an error if any but the last dp has no layover.
                report = None  # type: ignore

    def _start_dates(self, from_date: datetime, to_date: datetime) -> list[datetime]:
        """Builds a list of no-tz datetime representing start dates for trips."""
        calendar_entries = self._calendar_entries()
        days = int((to_date - from_date) / timedelta(days=1)) + 1
        if days != len(calendar_entries):
            raise ValueError(
                f"{days} days in range, but {len(calendar_entries)} entries "
                f"in calendar for trip {self!r}."
            )
        indexed_days = list(index_numeric_strings(calendar_entries))
        start_dates: list[datetime] = []
        for indexed in indexed_days:
            start_date = from_date + timedelta(days=indexed.idx)
            if start_date.day != int(indexed.txt):
                raise ValueError(
                    f"Error building date. start_date: {from_date}, "
                    f"day: {indexed.txt}, calendar_entries:{calendar_entries!r}"
                )
            start_dates.append(start_date)
        return start_dates

    def _resolve_start_dates(
        self, start_dates: list[datetime], airports: dict[str, Airport]
    ):
        """set the tz aware resolved start dates for this trip."""
        resolved_start_dates = []
        departure_station = self.dutyperiods[0].flights[0].departure_station().upper()
        tz_string = airports[departure_station].tz
        tz_info = ZoneInfo(tz_string)
        dep_time = self.dutyperiods[0].flights[0].departure_time()
        struct = time.strptime(dep_time.local, TIME)
        for start_date in start_dates:
            resolved_start_date = start_date.replace(
                tzinfo=tz_info, hour=struct.tm_hour, minute=struct.tm_min
            )
            resolved_start_dates.append(resolved_start_date)
        self.resolved_start_dates = resolved_start_dates

    def _calendar_entries(self) -> list[str]:
        """Make a list of the calendar entries for this trip."""
        calendar_strings: list[str] = []
        for dutyperiod in self.dutyperiods:
            calendar_strings.append(dutyperiod.report.calendar)
            for flight in dutyperiod.flights:
                calendar_strings.append(flight.flight.calendar)
            calendar_strings.append(dutyperiod.release.calendar)  # type: ignore
            if dutyperiod.layover:
                if dutyperiod.layover.hotel:
                    calendar_strings.append(dutyperiod.layover.hotel.calendar)
                if dutyperiod.layover.transportation:
                    calendar_strings.append(dutyperiod.layover.transportation.calendar)
                if dutyperiod.layover.hotel_additional:
                    calendar_strings.append(
                        dutyperiod.layover.hotel_additional.calendar
                    )
                if dutyperiod.layover.transportation_additional:
                    calendar_strings.append(
                        dutyperiod.layover.transportation_additional.calendar
                    )
        calendar_strings.append(self.footer.calendar)  # type: ignore
        calendar_entries: list[str] = []
        for entry in calendar_strings:
            calendar_entries.extend(entry.split())
        return calendar_entries


@dataclass
class Page(DataclassReprMixin):
    page_header_1: lines.PageHeader1
    page_header_2: lines.PageHeader2 | None = None
    base_equipment: lines.BaseEquipment | None = None
    page_footer: lines.PageFooter | None = None
    trips: List[Trip] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def effective(self) -> datetime:
        if self.page_footer is not None:
            return datetime.strptime(self.page_footer.effective, DATE)
        raise ValueError("Tried to get effective date, but page_footer was None.")

    def issued(self) -> datetime:
        if self.page_footer is not None:
            return datetime.strptime(self.page_footer.issued, DATE)
        raise ValueError("Tried to get issued date, but page_footer was None.")

    def base(self) -> str:
        return self.page_footer.base.upper()  # type: ignore

    def satelite_base(self) -> str:
        return self.page_footer.satelite_base.upper()  # type: ignore

    def from_to(self) -> tuple[datetime, datetime]:
        if self.page_header_2 is None:
            raise ValueError("Tried to get from_to but page_header_2 was None.")
        effective = self.effective()
        from_md = self.page_header_2.calendar_range[:5]
        to_md = self.page_header_2.calendar_range[6:]
        strf = MONTH_DAY
        from_date = complete_future_mdt(effective, from_md, strf=strf)
        to_date = complete_future_mdt(effective, to_md, strf=strf)
        return from_date, to_date

    def internal_page(self) -> str:
        if self.page_footer is None:
            raise ValueError("Tried to get internal_page but page_footer was None.")
        return self.page_footer.page

    def _line_range(self) -> str:
        if self.page_footer:
            to_line = self.page_footer.source.idx
        else:
            to_line = "UNDEFINED"
        return f"{self.page_header_1.source.idx}-{to_line}"

    def _source_lines(self) -> list[IndexedString]:
        source_lines: list[IndexedString] = []
        source_lines.append(self.page_header_1.source)
        if self.page_header_2:
            source_lines.append(self.page_header_2.source)
        if self.base_equipment:
            source_lines.append(self.base_equipment.source)
        for trip in self.trips:
            # pylint: disable=protected-access
            source_lines.extend(trip._source_lines())
        if self.page_footer:
            source_lines.append(self.page_footer.source)
        return source_lines


@dataclass
class Package(DataclassReprMixin):
    source: str
    # package_date: PackageDate | None
    pages: List[Page] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def from_to(self) -> tuple[datetime, datetime]:
        return self.pages[0].from_to()

    def base(self) -> str:
        return self.pages[0].base()

    def satelite_bases(self) -> Set[str]:
        bases: Set[str] = set()
        for page in self.pages:
            page_sat = page.satelite_base()
            if is_iata(page_sat):
                bases.add(page_sat)
        return bases

    def collect_iata_codes(self) -> Set[str]:
        iatas: set[str] = set()
        iatas.add(self.base())
        iatas.update(self.satelite_bases())
        for page in self.pages:
            for trip in page.trips:
                for dutyperiod in trip.dutyperiods:
                    for flight in dutyperiod.flights:
                        iatas.add(flight.departure_station())
                        iatas.add(flight.arrival_station())
        return iatas

    def resolve_package_dates(self, airports: dict[str, Airport]):
        """Resolve all the report, release, departure, and arrival times for the start dates."""
        for page in self.pages:
            from_date, to_date = page.from_to()
            for trip in page.trips:
                trip.resolve_all_the_dates(
                    from_date=from_date, to_date=to_date, airports=airports
                )


def is_iata(iata: str) -> bool:
    if isinstance(iata, str) and len(iata) == 3:
        return True
    return False


def parse_time(time_str: str) -> time.struct_time:
    struct = time.strptime(time_str, TIME)
    return struct


def parse_duration(dur_str: str) -> timedelta:
    delta = regex_parse_duration(DURATION_PATTERN, dur_str).to_timedelta()
    return delta
