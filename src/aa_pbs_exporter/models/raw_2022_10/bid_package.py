# # pylint: disable=missing-module-docstring
# # pylint: disable=missing-class-docstring
# # pylint: disable=missing-function-docstring

# import json
# import time
# from dataclasses import asdict, dataclass, field
# from datetime import datetime, timedelta
# from typing import Any, List, Set
# from uuid import UUID, uuid5
# from zoneinfo import ZoneInfo

# from aa_pbs_exporter import PROJECT_NAMESPACE
# from aa_pbs_exporter.airports.airport_model import Airport
# from aa_pbs_exporter.airports.airports import by_iata
# from aa_pbs_exporter.models.raw_2022_10 import lines
# from aa_pbs_exporter.snippets.datetime.complete_partial_datetime import (
#     complete_future_mdt,
#     complete_future_time,
# )
# from aa_pbs_exporter.snippets.datetime.parse_duration_regex import (
#     parse_duration as regex_parse_duration,
# )
# from aa_pbs_exporter.snippets.datetime.parse_duration_regex import pattern_HHHMM
# from aa_pbs_exporter.snippets.parsing.indexed_string import IndexedString
# from aa_pbs_exporter.snippets.string.index_numeric_strings import index_numeric_strings

# DATE = "%d%b%Y"
# TIME = "%H%M"
# MONTH_DAY = "%m/%d"
# DURATION_PATTERN = pattern_HHHMM(hm_sep=".")

# TAB = "\t"
# NL = "\n"


# @dataclass
# class ResolvedDepartArrive:
#     resolved_trip_start: datetime
#     departure: datetime
#     arrival: datetime


# @dataclass
# class ResolvedReportRelease:
#     resolved_trip_start: datetime
#     report: datetime
#     release: datetime


# @dataclass
# class LocalHbt:
#     local: str
#     hbt: str


# @dataclass
# class Flight:
#     flight: lines.Flight
#     resolved_flights: dict[datetime, ResolvedDepartArrive] = field(default_factory=dict)
#     cached_values: dict[str, Any] = field(default_factory=dict)

#     def __str__(self) -> str:
#         return self._indent_str()

#     def _indent_str(self, indent: str = "  ", indent_level: int = 0) -> str:
#         return (
#             f"{indent*indent_level}Flight:"
#             f"\n{self.flight._indent_str(indent,indent_level+1)}"
#             f"\n{indent*(indent_level+1)}resolved_flights: {self.resolved_flights!r}"
#             f"\n{indent*(indent_level+1)}cached_values: {self.cached_values!r}"
#         )

#     def dp_idx(self) -> str:
#         return self.flight.dutyperiod_idx

#     def dep_arr_day(self) -> str:
#         return self.flight.dep_arr_day

#     def eq_code(self) -> str:
#         return self.flight.eq_code

#     def number(self) -> str:
#         return self.flight.flight_number

#     def deadhead(self) -> bool:
#         return bool(self.flight.deadhead)

#     def departure_station(self) -> str:
#         return self.flight.departure_station.upper()

#     def departure_time(self) -> LocalHbt:
#         local, hbt = self.flight.departure_time.split("/")
#         return LocalHbt(local, hbt)

#     def resolved_departure_time(self, resolved_report: datetime) -> str:
#         raise NotImplementedError

#     def meal(self) -> str:
#         return self.flight.meal.upper()

#     def arrival_station(self) -> str:
#         return self.flight.arrival_station.upper()

#     def arrival_time(self) -> LocalHbt:
#         local, hbt = self.flight.arrival_time.split("/")
#         return LocalHbt(local, hbt)

#     def block(self) -> timedelta:
#         assert self.flight is not None
#         return self._cached_duration("block", self.flight.block)

#     def synth(self) -> timedelta:
#         assert self.flight is not None
#         return self._cached_duration("synth", self.flight.synth)

#     def ground(self) -> timedelta:
#         assert self.flight is not None
#         return self._cached_duration("ground", self.flight.ground)

#     def equipment_change(self) -> bool:
#         return bool(self.equipment_change)

#     def _cached_duration(self, key: str, raw_str: str) -> timedelta:
#         cached_value = self.cached_values.get(key, None)
#         if cached_value is None:
#             cached_value = parse_duration(raw_str)
#             self.cached_values[key] = cached_value
#         return cached_value


# @dataclass
# class Layover:
#     hotel: lines.Hotel
#     transportation: lines.Transportation | None = None
#     hotel_additional: lines.HotelAdditional | None = None
#     transportation_additional: lines.TransportationAdditional | None = None
#     cached_values: dict[str, Any] = field(default_factory=dict)

#     def __str__(self) -> str:
#         return self._indent_str()

#     def _indent_str(self, indent: str = "  ", indent_level: int = 0):
#         if self.transportation:
#             transportation = self.transportation._indent_str(indent, indent_level + 1)
#         else:
#             transportation = f"{indent*(indent_level+1)}No transportation"
#         if self.hotel_additional:
#             add_hotel = self.hotel_additional._indent_str(indent, indent_level + 1)
#         else:
#             add_hotel = f"{indent*(indent_level+1)}No additional hotel"
#         if self.transportation_additional:
#             add_trans = self.transportation_additional._indent_str(
#                 indent, indent_level + 1
#             )
#         else:
#             add_trans = f"{indent*(indent_level+1)}No additional transportation"
#         return (
#             f"{indent*indent_level}Layover:"
#             f"\n{self.hotel._indent_str(indent,indent_level+1)}"
#             f"\n{transportation}"
#             f"\n{add_hotel}"
#             f"\n{add_trans}"
#             f"\n{indent*(indent_level+1)}cached_values: {self.cached_values!r}"
#         )

#     def city(self) -> str:
#         return self.hotel.layover_city

#     def rest(self) -> timedelta:
#         assert self.hotel is not None
#         return self._cached_duration("rest", self.hotel.rest)

#     def hotel_name(self) -> str:
#         return self.hotel.name

#     def hotel_phone(self) -> str:
#         return self.hotel.phone or ""

#     def transportation_name(self) -> str:
#         if self.transportation is None:
#             return ""
#         return self.transportation.name

#     def transportation_phone(self) -> str:
#         if self.transportation is None:
#             return ""
#         return self.transportation.phone

#     def hotel_additional_name(self) -> str:
#         if self.hotel_additional is None:
#             return ""
#         return self.hotel_additional.name

#     def hotel_additional_phone(self) -> str:
#         if self.hotel_additional is None:
#             return ""
#         return self.hotel_additional.phone

#     def transportation_additional_name(self) -> str:
#         if self.transportation_additional is None:
#             return ""
#         return self.transportation_additional.name

#     def transportation_additional_phone(self) -> str:
#         if self.transportation_additional is None:
#             return ""
#         return self.transportation_additional.phone

#     def _cached_duration(self, key: str, raw_str: str) -> timedelta:
#         cached_value = self.cached_values.get(key, None)
#         if cached_value is None:
#             cached_value = parse_duration(raw_str)
#             self.cached_values[key] = cached_value
#         return cached_value


# @dataclass
# class DutyPeriod:
#     report: lines.DutyPeriodReport
#     release: lines.DutyPeriodRelease | None = None
#     layover: Layover | None = None
#     flights: List[Flight] = field(default_factory=list)
#     resolved_reports: dict[datetime, ResolvedReportRelease] = field(
#         default_factory=dict
#     )
#     cached_values: dict[str, Any] = field(default_factory=dict)

#     def __str__(self) -> str:
#         return self._indent_str()

#     def _indent_str(self, indent: str = "  ", indent_level: int = 0) -> str:
#         if self.release is not None:
#             release = self.release._indent_str(indent, indent_level + 2)
#         else:
#             release = f"{indent*(indent_level+2)}No release"
#         if self.layover is not None:
#             layover = f"{self.layover._indent_str(indent,indent_level+1)}"
#         else:
#             layover = f"{indent*(indent_level+2)}No layover"
#         flight_strings = []
#         for flight in self.flights:
#             flight_strings.append(f"{flight._indent_str(indent,indent_level+2)}")
#         return (
#             f"{indent*indent_level}DutyPeriod:"
#             f"\n{indent*(indent_level+1)}Report:"
#             f"\n{self.report._indent_str(indent,indent_level+2)}"
#             f"\n{indent*(indent_level+1)}Flights:"
#             f"\n{NL.join(flight_strings)}"
#             f"\n{indent*(indent_level+1)}Release:"
#             f"\n{release}"
#             # f"\n{indent*(indent_level+1)}Layover:"
#             f"\n{layover}"
#             f"\n{indent*(indent_level+1)}resolved_reports: {self.resolved_reports!r}"
#             f"\n{indent*(indent_level+1)}cached_values: {self.cached_values!r}"
#         )

#     def report_time(self) -> LocalHbt:
#         local, hbt = self.report.report.split("/")
#         return LocalHbt(local, hbt)

#     def report_station(self) -> str:
#         return self.flights[0].departure_station()

#     def release_time(self) -> LocalHbt:
#         assert self.release is not None
#         local, hbt = self.release.release.split("/")
#         return LocalHbt(local, hbt)

#     def release_station(self) -> str:
#         return self.flights[-1].arrival_station()

#     def block(self) -> timedelta:
#         assert self.release is not None
#         return self._cached_duration("block", self.release.block)

#     def synth(self) -> timedelta:
#         assert self.release is not None
#         return self._cached_duration("synth", self.release.synth)

#     def pay(self) -> timedelta:
#         assert self.release is not None
#         return self._cached_duration("total_pay", self.release.total_pay)

#     def duty(self) -> timedelta:
#         assert self.release is not None
#         return self._cached_duration("duty", self.release.duty)

#     def flight_duty(self) -> timedelta:
#         assert self.release is not None
#         return self._cached_duration("flight_duty", self.release.flight_duty)

#     def _sum_flight_durations(self, resolved_start_date: datetime) -> timedelta:
#         """Total time from start of first flight to end of last flight.

#         dutyperiod and flights must be complete before calling this function.
#         """
#         total = timedelta()
#         for flight in self.flights:
#             total = total + (
#                 flight.resolved_flights[resolved_start_date].arrival
#                 - flight.resolved_flights[resolved_start_date].departure
#             )
#             total = total + flight.ground()
#         return total

#     def _cached_duration(self, key: str, raw_str: str) -> timedelta:
#         cached_value = self.cached_values.get(key, None)
#         if cached_value is None:
#             cached_value = parse_duration(raw_str)
#             self.cached_values[key] = cached_value
#         return cached_value

#     def _source_lines(self) -> list[IndexedString]:
#         source_lines: list[IndexedString] = []
#         source_lines.append(self.report.source)
#         for flight in self.flights:
#             source_lines.append(flight.flight.source)
#         if self.release:
#             source_lines.append(self.release.source)
#         if self.layover:
#             source_lines.append(self.layover.hotel.source)
#             if value := self.layover.transportation:
#                 source_lines.append(value.source)
#             if self.layover.hotel_additional:
#                 source_lines.append(self.layover.hotel_additional.source)
#             if self.layover.transportation_additional:
#                 source_lines.append(self.layover.transportation_additional.source)
#         return source_lines

#     def complete_dutyperiod(
#         self, resolved_trip_start: datetime, airports: dict[str, Airport]
#     ):
#         """Resolve the dutyperiods flight departure and arrival times.

#         The dutyperiod's resolved report and release times are expected to be in
#         self.resolved_reports
#         """
#         resolved_report = self.resolved_reports[resolved_trip_start].report
#         self._resolve_flights(
#             resolved_trip_start=resolved_trip_start,
#             resolved_report=resolved_report,
#             airports=airports,
#         )

#     def _resolve_flights(
#         self,
#         resolved_trip_start: datetime,
#         resolved_report: datetime,
#         airports: dict[str, Airport],
#     ):
#         """Resolve flight departure and arrival times for the start date."""
#         depart_lcl = self.flights[0].departure_time().local
#         departure_tz = airports[self.flights[0].departure_station()].tz
#         # next_departure is updated each loop.
#         next_departure: datetime = complete_future_time(
#             resolved_report, depart_lcl, tz_info=ZoneInfo(departure_tz), strf=TIME
#         )
#         for idx, flight in enumerate(self.flights):
#             if flight.block() > timedelta():
#                 arrival = next_departure + flight.block()
#             elif flight.synth() > timedelta():
#                 arrival = next_departure + flight.synth()
#             else:
#                 raise ValueError(
#                     f"block and synth are 0, unable to compute arrival time.\n{flight=}\n"
#                 )
#             arrival_tz = airports[flight.arrival_station()].tz
#             arrival = arrival.astimezone(ZoneInfo(arrival_tz))
#             flight.resolved_flights[resolved_trip_start] = ResolvedDepartArrive(
#                 resolved_trip_start=resolved_trip_start,
#                 departure=next_departure,
#                 arrival=arrival,
#             )

#             if idx + 1 < len(self.flights):
#                 ground = flight.ground()
#                 next_departure = arrival + ground
#             else:
#                 # this is the last time through the loop, all dates should be resolved.
#                 # set an impossible date just to make the typecheckers happy, and
#                 # make it obvious during validation if it somehow slips through.
#                 next_departure = datetime(*(1900, 1, 1))


# @dataclass
# class Trip:
#     header: lines.TripHeader
#     footer: lines.TripFooter | None = None
#     dutyperiods: List[DutyPeriod] = field(default_factory=list)
#     resolved_start_dates: list[datetime] = field(default_factory=list)
#     cached_values: dict[str, Any] = field(default_factory=dict)

#     def __str__(self) -> str:
#         return self._indent_str()

#     def _indent_str(self, indent: str = "  ", indent_level: int = 0):
#         if self.footer:
#             footer = self.footer._indent_str(indent, indent_level + 2)
#         else:
#             footer = f"{indent*(indent_level+2)}No footer"
#         dp_strings = []
#         for dutyperiod in self.dutyperiods:
#             dp_strings.append(dutyperiod._indent_str(indent, indent_level + 2))
#         return (
#             f"{indent*indent_level}Trip:"
#             f"\n{indent*(indent_level+1)}Header:"
#             f"\n{self.header._indent_str(indent,indent_level+2)}"
#             f"\n{indent*(indent_level+1)}DutyPeriods:"
#             f"\n{NL.join(dp_strings)}"
#             f"\n{indent*(indent_level+1)}Footer:"
#             f"\n{footer}"
#             f"\n{indent*(indent_level+1)}resolved_start_dates: {self.resolved_start_dates!r}:"
#             f"\n{indent*(indent_level+1)}cached_values: {self.cached_values!r}:"
#         )

#     def uuid(self, resolved_start_date: datetime) -> UUID:
#         cached_value = self.cached_values.get("hash_string", None)
#         if cached_value is None:
#             cached_value = (
#                 f"{json.dumps(asdict(self.header))}"
#                 f"{json.dumps(asdict(self.footer))}"
#                 # f"{json.dumps(list([asdict(x) for x in self.dutyperiods]))}"
#             )
#             self.cached_values["hash_string"] = cached_value
#         value = f"{resolved_start_date.isoformat()}{cached_value}"
#         return uuid5(PROJECT_NAMESPACE, value)

#     def number(self) -> str:
#         return self.header.number

#     def ops_count(self) -> str:
#         return self.header.ops_count

#     def base(self, page: "Page") -> str:
#         return page.base()

#     def satelite_base(self, page: "Page") -> str:
#         return page.satelite_base()

#     def positions(self) -> str:
#         return self.header.positions

#     def operations(self) -> str:
#         return self.header.operations

#     def division(self, page: "Page") -> str:
#         return page.division()

#     def equipment(self, page: "Page") -> str:
#         return page.equipment()

#     def special_qualification(self) -> bool:
#         return bool(self.header.special_qualification)

#     def _cached_duration(self, key: str, raw_str: str) -> timedelta:
#         cached_value = self.cached_values.get(key, None)
#         if cached_value is None:
#             cached_value = parse_duration(raw_str)
#             self.cached_values[key] = cached_value
#         return cached_value

#     def block(self) -> timedelta:
#         assert self.footer is not None
#         return self._cached_duration("block", self.footer.block)

#     def synth(self) -> timedelta:
#         assert self.footer is not None
#         return self._cached_duration("synth", self.footer.synth)

#     def pay(self) -> timedelta:
#         assert self.footer is not None
#         return self._cached_duration("total_pay", self.footer.total_pay)

#     def tafb(self) -> timedelta:
#         assert self.footer is not None
#         return self._cached_duration("tafb", self.footer.tafb)

#     def complete_trip(
#         self, from_date: datetime, to_date: datetime, airports: dict[str, Airport]
#     ):
#         """Resolve all the report, release, departure, and arrival dates for each start date."""
#         start_dates = self._collect_start_dates(from_date=from_date, to_date=to_date)
#         self.cached_values["start_dates"] = start_dates
#         self._resolve_trip_start_dates(start_dates=start_dates, airports=airports)
#         for start in self.resolved_start_dates:
#             self._resolve_dutyperiods(start, airports=airports)

#     def _line_range(self) -> str:
#         """The start and end line in the source text for this trip."""
#         if self.footer:
#             to_line = self.footer.source.idx
#         else:
#             to_line = "UNDEFINED"
#         return f"{self.header.source.idx}-{to_line}"

#     def _source_lines(self) -> list[IndexedString]:
#         source_lines: list[IndexedString] = []
#         source_lines.append(self.header.source)
#         for dutyperiod in self.dutyperiods:
#             # pylint: disable=protected-access
#             source_lines.extend(dutyperiod._source_lines())
#         if self.footer:
#             source_lines.append(self.footer.source)
#         return source_lines

#     def _resolve_dutyperiods(
#         self, resolved_start_date: datetime, airports: dict[str, Airport]
#     ):
#         """Calculate resolved report, release, departure, and arrival.

#         Complete calculations by adding up times as necessary.

#         """
#         first_report_time = parse_time(self.dutyperiods[0].report_time().local)
#         # next_report is updated each pass through the loop.
#         next_report: datetime = resolved_start_date.replace(
#             hour=first_report_time.tm_hour, minute=first_report_time.tm_min
#         )
#         for idx, dutyperiod in enumerate(self.dutyperiods):
#             release_tz: str = airports[dutyperiod.release_station()].tz
#             release = next_report + dutyperiod.duty()
#             release = release.astimezone(ZoneInfo(release_tz))
#             resolved = ResolvedReportRelease(
#                 resolved_trip_start=resolved_start_date,
#                 report=next_report,
#                 release=release,
#             )
#             dutyperiod.resolved_reports[resolved.resolved_trip_start] = resolved
#             dutyperiod.complete_dutyperiod(
#                 resolved_trip_start=resolved_start_date,
#                 airports=airports,
#             )
#             if idx + 1 < len(self.dutyperiods):
#                 assert dutyperiod.layover is not None
#                 next_report = release + dutyperiod.layover.rest()
#             else:
#                 # this is the last time through the loop, all dates should be resolved.
#                 # set an impossible date just to make the typecheckers happy, and
#                 # make it obvious during validation if it somehow slips through.
#                 next_report = datetime(*(1900, 1, 1))

#     def _collect_start_dates(
#         self, from_date: datetime, to_date: datetime
#     ) -> list[datetime]:
#         """Builds a list of no-tz datetime representing start dates for trips."""
#         calendar_entries = self._calendar_entries()
#         self.cached_values["calendar_entries"] = calendar_entries
#         days = int((to_date - from_date) / timedelta(days=1)) + 1
#         if days != len(calendar_entries):
#             raise ValueError(
#                 f"{days} days in range, but {len(calendar_entries)} entries "
#                 f"in calendar for trip {self!r}."
#             )
#         indexed_days = list(index_numeric_strings(calendar_entries))
#         if len(indexed_days) != int(self.ops_count()):
#             raise ValueError(
#                 f"Expected {self.ops_count()} dates, but found {indexed_days} in calendar {calendar_entries}"
#             )
#         start_dates: list[datetime] = []
#         for indexed in indexed_days:
#             start_date = from_date + timedelta(days=indexed.idx)
#             if start_date.day != int(indexed.txt):
#                 raise ValueError(
#                     f"Error building date. start_date: {from_date}, "
#                     f"day: {indexed.txt}, calendar_entries:{calendar_entries!r}"
#                 )
#             start_dates.append(start_date)
#         # print(f"Trip: {self.number()}, start dates: {start_dates}")
#         return start_dates

#     def _resolve_trip_start_dates(
#         self, start_dates: list[datetime], airports: dict[str, Airport]
#     ):
#         """set the tz aware resolved start dates for this trip."""
#         resolved_start_dates = []
#         departure_station = self.dutyperiods[0].flights[0].departure_station().upper()
#         departure_tz = airports[departure_station].tz
#         tz_info = ZoneInfo(departure_tz)
#         dep_time = self.dutyperiods[0].flights[0].departure_time()
#         struct = time.strptime(dep_time.local, TIME)
#         for start_date in start_dates:
#             resolved_start_date = start_date.replace(
#                 tzinfo=tz_info, hour=struct.tm_hour, minute=struct.tm_min
#             )
#             resolved_start_dates.append(resolved_start_date)
#         self.resolved_start_dates = resolved_start_dates

#     def _calendar_entries(self) -> list[str]:
#         """Make a list of the calendar entries for this trip."""
#         calendar_strings: list[str] = []
#         for dutyperiod in self.dutyperiods:
#             calendar_strings.append(dutyperiod.report.calendar)
#             for flight in dutyperiod.flights:
#                 calendar_strings.append(flight.flight.calendar)
#             assert dutyperiod.release is not None
#             calendar_strings.append(dutyperiod.release.calendar)
#             if dutyperiod.layover:
#                 if dutyperiod.layover.hotel:
#                     calendar_strings.append(dutyperiod.layover.hotel.calendar)
#                 if dutyperiod.layover.transportation:
#                     calendar_strings.append(dutyperiod.layover.transportation.calendar)
#                 if dutyperiod.layover.hotel_additional:
#                     calendar_strings.append(
#                         dutyperiod.layover.hotel_additional.calendar
#                     )
#                 if dutyperiod.layover.transportation_additional:
#                     calendar_strings.append(
#                         dutyperiod.layover.transportation_additional.calendar
#                     )
#         assert self.footer is not None
#         calendar_strings.append(self.footer.calendar)
#         calendar_entries: list[str] = []
#         for entry in calendar_strings:
#             calendar_entries.extend(entry.split())
#         return calendar_entries


# @dataclass
# class Page:
#     page_header_1: lines.PageHeader1
#     page_header_2: lines.PageHeader2 | None = None
#     base_equipment: lines.BaseEquipment | None = None
#     page_footer: lines.PageFooter | None = None
#     trips: List[Trip] = field(default_factory=list)

#     def effective(self) -> datetime:
#         if self.page_footer is not None:
#             return datetime.strptime(self.page_footer.effective, DATE)
#         raise ValueError("Tried to get effective date, but page_footer was None.")

#     def issued(self) -> datetime:
#         if self.page_footer is not None:
#             return datetime.strptime(self.page_footer.issued, DATE)
#         raise ValueError("Tried to get issued date, but page_footer was None.")

#     def division(self) -> str:
#         assert self.page_footer is not None
#         return self.page_footer.division

#     def equipment(self) -> str:
#         assert self.page_footer is not None
#         return self.page_footer.equipment

#     def base(self) -> str:
#         assert self.page_footer is not None
#         return self.page_footer.base.upper()

#     def satelite_base(self) -> str:
#         assert self.page_footer is not None
#         return self.page_footer.satelite_base.upper()

#     def from_to(self) -> tuple[datetime, datetime]:
#         if self.page_header_2 is None:
#             raise ValueError("Tried to get from_to but page_header_2 was None.")
#         effective = self.effective()
#         from_md = self.page_header_2.calendar_range[:5]
#         to_md = self.page_header_2.calendar_range[6:]
#         strf = MONTH_DAY
#         from_date = complete_future_mdt(effective, from_md, strf=strf)
#         to_date = complete_future_mdt(effective, to_md, strf=strf)
#         return from_date, to_date

#     def internal_page(self) -> str:
#         if self.page_footer is None:
#             raise ValueError("Tried to get internal_page but page_footer was None.")
#         return self.page_footer.page

#     def complete_page(self, airports: dict[str, Airport]):
#         from_date, to_date = self.from_to()
#         for trip in self.trips:
#             trip.complete_trip(from_date=from_date, to_date=to_date, airports=airports)

#     def _line_range(self) -> str:
#         if self.page_footer:
#             to_line = self.page_footer.source.idx
#         else:
#             to_line = "UNDEFINED"
#         return f"{self.page_header_1.source.idx}-{to_line}"

#     def _source_lines(self) -> list[IndexedString]:
#         source_lines: list[IndexedString] = []
#         source_lines.append(self.page_header_1.source)
#         if self.page_header_2:
#             source_lines.append(self.page_header_2.source)
#         if self.base_equipment:
#             source_lines.append(self.base_equipment.source)
#         for trip in self.trips:
#             # pylint: disable=protected-access
#             source_lines.extend(trip._source_lines())
#         if self.page_footer:
#             source_lines.append(self.page_footer.source)
#         return source_lines


# @dataclass
# class Package:
#     source: str
#     # package_date: PackageDate | None
#     pages: List[Page] = field(default_factory=list)
#     airports: dict[str, Airport] = field(default_factory=dict)

#     def from_to(self) -> tuple[datetime, datetime]:
#         return self.pages[0].from_to()

#     def base(self) -> str:
#         return self.pages[0].base()

#     def satelite_bases(self) -> Set[str]:
#         bases: Set[str] = set()
#         for page in self.pages:
#             page_sat = page.satelite_base()
#             if is_iata(page_sat):
#                 bases.add(page_sat)
#         return bases

#     def complete_package(self):
#         self._collect_airports()
#         self._resolve_package_dates()

#     def _collect_airports(self):
#         airports: dict[str, Airport] = {}
#         for iata in self._collect_iata_codes():
#             airports[iata] = by_iata(iata)
#         self.airports = airports
#         # bid_package.resolve_package_dates(airports=airports)

#     def _collect_iata_codes(self) -> Set[str]:
#         iatas: set[str] = set()
#         iatas.add(self.base())
#         iatas.update(self.satelite_bases())
#         for page in self.pages:
#             for trip in page.trips:
#                 for dutyperiod in trip.dutyperiods:
#                     for flight in dutyperiod.flights:
#                         iatas.add(flight.departure_station())
#                         iatas.add(flight.arrival_station())
#         return iatas

#     def _resolve_package_dates(self):
#         """Resolve all the report, release, departure, and arrival times for the start dates."""
#         for page in self.pages:
#             page.complete_page(airports=self.airports)


# def is_iata(iata: str) -> bool:
#     if isinstance(iata, str) and len(iata) == 3:
#         return True
#     return False


# def parse_time(time_str: str) -> time.struct_time:
#     struct = time.strptime(time_str, TIME)
#     return struct


# def parse_duration(dur_str: str) -> timedelta:
#     delta = regex_parse_duration(DURATION_PATTERN, dur_str).to_timedelta()
#     return delta
