# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Set
from zoneinfo import ZoneInfo

from aa_pbs_exporter.airports.airport_model import Airport
from aa_pbs_exporter.models.raw_2022_10 import raw_lines
from aa_pbs_exporter.util.complete_partial_datetime import (
    complete_future_mdt,
    complete_future_time,
)
from aa_pbs_exporter.util.dataclass_repr_mixin import DataclassReprMixin
from aa_pbs_exporter.util.index_numeric_strings import index_numeric_strings
from aa_pbs_exporter.util.parse_duration_regex import (
    parse_duration as regex_parse_duration,
)
from aa_pbs_exporter.util.parse_duration_regex import pattern_HHHMM

DATE = ""
TIME = ""
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
    flight: raw_lines.Flight
    resolved_flights: dict[datetime, ResolvedFlight] = field(default_factory=dict)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def dp_idx(self) -> str:
        return self.flight.dutyperiod_index

    def d_a(self) -> str:
        return self.flight.d_a

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

    def resolved_arrival_time(self, resolved_departure_time: datetime) -> str:
        raise NotImplementedError

    def block(self) -> timedelta:
        value = self.flight.block  # type: ignore
        return parse_duration(value)

    def synth(self) -> timedelta:
        value = self.flight.synth  # type: ignore
        return parse_duration(value)

    def ground(self) -> timedelta:
        value = self.flight.ground  # type: ignore
        return parse_duration(value)

    def equipment_change(self) -> bool:
        raise NotImplementedError


@dataclass
class Layover(DataclassReprMixin):
    hotel: raw_lines.Hotel
    transportation: raw_lines.Transportation | None = None
    hotel_additional: raw_lines.HotelAdditional | None = None
    transportation_additional: raw_lines.TransportationAdditional | None = None

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def city(self) -> str:
        return self.hotel.layover_city

    def rest(self) -> timedelta:
        value = self.hotel.rest  # type: ignore
        return parse_duration(value)

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


@dataclass
class DutyPeriod(DataclassReprMixin):
    report: raw_lines.DutyPeriodReport
    release: raw_lines.DutyPeriodRelease | None = None
    layover: Layover | None = None
    flights: List[Flight] = field(default_factory=list)
    resolved_reports: dict[datetime, ResolvedDutyperiod] = field(default_factory=dict)

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
        value = self.release.block  # type: ignore
        return parse_duration(value)

    def synth(self) -> timedelta:
        value = self.release.synth  # type: ignore
        return parse_duration(value)

    def pay(self) -> timedelta:
        value = self.release.total_pay  # type: ignore
        return parse_duration(value)

    def duty(self) -> timedelta:
        value = self.release.duty  # type: ignore
        return parse_duration(value)

    def flight_duty(self) -> timedelta:
        value = self.release.flight_duty  # type: ignore
        return parse_duration(value)

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
    header: raw_lines.TripHeader
    footer: raw_lines.TripFooter | None = None
    dutyperiods: List[DutyPeriod] = field(default_factory=list)
    resolved_start_dates: list[datetime] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

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

    def block(self) -> timedelta:
        value = self.footer.block  # type: ignore
        return parse_duration(value)

    def synth(self) -> timedelta:
        value = self.footer.synth  # type: ignore
        return parse_duration(value)

    def pay(self) -> timedelta:
        value = self.footer.total_pay  # type: ignore
        return parse_duration(value)

    def tafb(self) -> timedelta:
        value = self.footer.tafb  # type: ignore
        return parse_duration(value)

    def resolve_all_the_dates(
        self, from_date: datetime, to_date: datetime, airports: dict[str, Airport]
    ):
        """Resolve all the report, release, departure, and arrival dates for each start date."""
        start_dates = self._start_dates(from_date=from_date, to_date=to_date)
        self._resolve_start_dates(start_dates=start_dates, airports=airports)
        for start in self.resolved_start_dates:
            self._resolve_trip_dates(start, airports=airports)

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
            local_rpt = dutyperiod.report_time().local
            if report.strftime("%H%M") != local_rpt:
                raise ValueError(
                    f"{report.isoformat()} time does not "
                    f"match local report {local_rpt} {dutyperiod=}"
                )
            tz_string = airports[dutyperiod.release_station()].tz
            release = report + dutyperiod.duty()
            release = release.astimezone(ZoneInfo(tz_string))
            local_rls = dutyperiod.release_time().local
            if release.strftime("%H%M") != local_rls:
                raise ValueError(
                    f"{release.isoformat()} time does not match "
                    f"local release {local_rls} {dutyperiod=}"
                )
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
        tafb = self.tafb()
        if (
            tafb
            != self.dutyperiods[-1].release_time() - self.dutyperiods[0].report_time()
        ):
            raise ValueError(
                f"{tafb=} does not match trip release - trip report. start_date={resolved_start_date} trip={self}"
            )

    def _start_dates(self, from_date: datetime, to_date: datetime) -> list[datetime]:
        """Builds a list of no-tz datetime representing start dates for trips."""
        calendar_entries = self._calendar_entries()
        days = int((to_date - from_date) / timedelta(days=1)) + 1
        if days != len(calendar_entries):
            raise ValueError(
                f"{days} days in range, but {len(calendar_entries)} entries in calendar."
            )
        indexed_days = list(index_numeric_strings(calendar_entries))
        start_dates: list[datetime] = []
        for idx in indexed_days:
            start_date = from_date + timedelta(days=idx.idx)
            if start_date.day != int(idx.str_value):
                raise ValueError(
                    f"Error building date. start_date: {from_date}, "
                    f"day: {idx.str_value}, calendar_entries:{calendar_entries!r}"
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
        local = self.dutyperiods[0].flights[0].departure_time_local()
        struct = time.strptime(local, TIME)
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
                calendar_strings.append(flight.calendar)
            calendar_strings.append(dutyperiod.release.calendar)  # type: ignore
            if dutyperiod.hotel:
                calendar_strings.append(dutyperiod.hotel.calendar)
            if dutyperiod.transportation:
                calendar_strings.append(dutyperiod.transportation.calendar)
            if dutyperiod.hotel_additional:
                calendar_strings.append(dutyperiod.hotel_additional.calendar)
            if dutyperiod.transportation_additional:
                calendar_strings.append(dutyperiod.transportation_additional.calendar)
        calendar_strings.append(self.footer.calendar)  # type: ignore
        calendar_entries: list[str] = []
        for entry in calendar_strings:
            calendar_entries.extend(entry.split())
        return calendar_entries


@dataclass
class Page(DataclassReprMixin):
    page_header_1: raw_lines.PageHeader1
    page_header_2: raw_lines.PageHeader2 | None = None
    base_equipment: raw_lines.BaseEquipment | None = None
    page_footer: raw_lines.PageFooter | None = None
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
        strf = "%m/%d"
        from_date = complete_future_mdt(effective, from_md, strf=strf)
        to_date = complete_future_mdt(effective, to_md, strf=strf)
        return from_date, to_date


@dataclass
class Package(DataclassReprMixin):
    file_name: str
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
