from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
from typing import List, Set
from zoneinfo import ZoneInfo

from aa_pbs_exporter.airports.airport_model import Airport
from aa_pbs_exporter.models.raw_2022_10 import raw_lines
from aa_pbs_exporter.util.complete_partial_datetime import complete_future_mdt
from aa_pbs_exporter.util.dataclass_repr_mixin import DataclassReprMixin
from aa_pbs_exporter.util.index_numeric_strings import index_numeric_strings
from aa_pbs_exporter.util.parse_duration_regex import (
    parse_duration as regex_parse_duration,
)
from aa_pbs_exporter.util.parse_duration_regex import pattern_HHHMM

DATE = ""
TIME = ""
DURATION_PATTERN = pattern_HHHMM(hm_sep=".")
# TODO make Layover class, refactor


@dataclass
class Flight(DataclassReprMixin):
    flight: raw_lines.Flight

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

    def departure_time(self) -> tuple[str, str]:
        local, hbt = self.flight.departure_time.split("/")
        return local, hbt

    def resolved_departure_time(self, resolved_report: datetime) -> str:
        raise NotImplementedError

    def meal(self) -> str:
        return self.flight.meal.upper()

    def arrival_station(self) -> str:
        return self.flight.arrival_station.upper()

    def arrival_time(self) -> tuple[str, str]:
        local, hbt = self.flight.arrival_time.split("/")
        return local, hbt

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

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def resolved_report_time(
        self, resolved_start_date: datetime, trip: "Trip", airports: dict[str, Airport]
    ) -> datetime:
        raise NotImplementedError

    def resolved_release_time(
        self, resolved_report: datetime, airports: dict[str, Airport]
    ):
        raise NotImplementedError

    def report_station(self) -> str:
        return self.flights[0].departure_station()

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

    def collect_departure_arrival(
        self, resolved_report_time: datetime, airports: dict[str, Airport]
    ) -> list[tuple[datetime, datetime, Flight]]:
        """Collect departure and arrival times for flights by adding block and ground times."""
        raise NotImplementedError


@dataclass
class Trip(DataclassReprMixin):
    header: raw_lines.TripHeader
    footer: raw_lines.TripFooter | None = None
    dutyperiods: List[DutyPeriod] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def number(self) -> str:
        return self.header.number

    def ops_count(self) -> str:
        return self.header.ops_count

    def base(self, page: "Page") -> str:
        return page.page_footer.base  # type: ignore

    def satelite_base(self, page: "Page") -> str | None:
        return page.page_footer.satelite_base  # type: ignore

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

    def collected_report_release(
        self, start_date: datetime, airports: dict[str, Airport]
    ) -> list[tuple[datetime, datetime, DutyPeriod]]:
        """Calculate resolved report and release by adding duty and rest for dutyperiods."""
        raise NotImplementedError

    def start_dates(self, from_date: datetime, to_date: datetime) -> list[datetime]:
        calendar_entries = self.calendar_entries()
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

    def resolved_start_dates(
        self, start_dates: list[datetime], airports: dict[str, Airport]
    ) -> list[datetime]:
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
        return resolved_start_dates

    def calendar_entries(self) -> list[str]:
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

    def collect_iata_codes(self) -> Set[str]:
        iatas: set[str] = set()
        for page in self.pages:
            for trip in page.trips:
                for dutyperiod in trip.dutyperiods:
                    for flight in dutyperiod.flights:
                        iatas.add(flight.departure_station())
                        iatas.add(flight.arrival_station())
        if None in iatas:
            iatas.remove(None)  # type: ignore
        if "" in iatas:
            iatas.remove("")
        return iatas


def parse_duration(dur_str: str) -> timedelta:
    delta = regex_parse_duration(DURATION_PATTERN, dur_str).to_timedelta()
    return delta
