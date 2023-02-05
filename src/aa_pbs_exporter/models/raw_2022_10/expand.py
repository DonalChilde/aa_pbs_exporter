# import time
# from dataclasses import dataclass, field
# from datetime import datetime, timedelta
# from zoneinfo import ZoneInfo

# from aa_pbs_exporter.airports.airport_model import Airport

# # from aa_pbs_exporter.models.raw_2022_10 import bid_package as raw_bid
# from aa_pbs_exporter.models.raw_2022_10 import lines_copy as raw_lines
# from aa_pbs_exporter.snippets.datetime.complete_partial_datetime import (
#     complete_future_mdt,
#     complete_future_time,
# )
# from aa_pbs_exporter.snippets.datetime.parse_duration_regex import (
#     parse_duration as regex_parse_duration,
# )
# from aa_pbs_exporter.snippets.datetime.parse_duration_regex import pattern_HHHMM
# from aa_pbs_exporter.snippets.string.index_numeric_strings import index_numeric_strings

# DURATION_PATTERN = pattern_HHHMM(hm_sep=".")
# TIME = "%H%M"
# DATE = "%d%b%Y"
# MONTH_DAY = "%m/%d"

# # TODO make validator class to allow passing out validation messages
# # TODO split to expanded model, and expand functions? rename?
# # TODO decide on parser version scheme, and rename packages
# #   - pbs_2022_10
# #       - parse
# #       - models
# #           - raw
# #           - expanded
# #       - validate
# #       - convert

# # class LocalHbt(TypedDict):
# #     local: str
# #     hbt: str


# @dataclass
# class SourceReference:
#     source: str
#     from_line: int
#     to_line: int


# @dataclass
# class Transportation:
#     name: str
#     phone: str


# @dataclass
# class Hotel:
#     name: str
#     phone: str | None


# @dataclass
# class Layover:
#     odl: timedelta
#     city: str
#     hotel: Hotel | None
#     transportation: Transportation | None
#     hotel_additional: Hotel | None
#     transportation_additional: Transportation | None


# @dataclass
# class Flight:
#     dutyperiod_idx: int
#     idx: int
#     dep_arr_day: str
#     eq_code: str
#     number: str
#     deadhead: bool
#     departure_station: str
#     departure_time: datetime
#     meal: str
#     arrival_station: str
#     arrival_time: datetime
#     block: timedelta
#     synth: timedelta
#     ground: timedelta
#     equipment_change: bool


# @dataclass
# class DutyPeriod:
#     idx: int
#     report: datetime
#     report_station: str
#     release: datetime
#     release_station: str
#     block: timedelta
#     synth: timedelta
#     total_pay: timedelta
#     duty: timedelta
#     flight_duty: timedelta
#     layover: Layover | None
#     flights: list[Flight] = field(default_factory=list)


# @dataclass
# class Trip:
#     # uuid: UUID
#     number: str
#     # base: str
#     # satelite_base: str
#     positions: str
#     operations: str
#     # division: str
#     # equipment: str
#     special_qualifications: bool
#     block: timedelta
#     synth: timedelta
#     total_pay: timedelta
#     tafb: timedelta
#     # source_ref: SourceReference | None
#     dutyperiods: list[DutyPeriod] = field(default_factory=list)


# @dataclass
# class Page:
#     base: str
#     satellite_base: str
#     equipment: str
#     division: str
#     issued: datetime
#     effective: datetime
#     start: datetime
#     end: datetime
#     trips: list[Trip] = field(default_factory=list)


# @dataclass
# class BidPackage:
#     source: str
#     pages: list[Page] = field(default_factory=list)


# def expand_bid_package(
#     bid_package: raw_lines.Package, airports: dict[str, Airport]
# ) -> BidPackage:
#     expanded_pages: list[Page] = []
#     for page in bid_package.pages:
#         expanded_pages.append(expand_page(page, airports))

#     expanded_bid_package = BidPackage(source=bid_package.source, pages=expanded_pages)
#     return expanded_bid_package


# def expand_page(page: raw_lines.Page, airports: dict[str, Airport]) -> Page:

#     assert page.page_footer is not None
#     assert page.page_header_2 is not None
#     effective = datetime.strptime(page.page_footer.effective, DATE)
#     start, end = get_from_to(
#         effective=effective, calendar_range=page.page_header_2.calendar_range
#     )
#     expanded_page = Page(
#         base=page.page_footer.base,
#         satellite_base=page.page_footer.satelite_base,
#         equipment=page.page_footer.equipment,
#         division=page.page_footer.division,
#         issued=datetime.strptime(page.page_footer.issued, DATE),
#         effective=effective,
#         start=start,
#         end=end,
#         trips=expand_trips(
#             trips=page.trips, from_date=start, to_date=end, airports=airports
#         ),
#     )
#     return expanded_page


# def expand_trips(
#     trips: list[raw_lines.Trip],
#     from_date: datetime,
#     to_date: datetime,
#     airports: dict[str, Airport],
# ) -> list[Trip]:
#     expanded_trips: list[Trip] = []
#     for trip in trips:
#         calendar_entries = get_calendar_entries(trip)
#         start_dates = get_start_dates(
#             from_date=from_date, to_date=to_date, calendar_entries=calendar_entries
#         )
#         expanded_trips.extend(expand_trip(trip, start_dates, airports))
#     return expanded_trips


# def expand_trip(
#     trip: raw_lines.Trip, start_dates: list[datetime], airports: dict[str, Airport]
# ) -> list[Trip]:
#     trips: list[Trip] = []
#     for start in start_dates:
#         first_report_lcl, _ = trip.dutyperiods[0].report.report.split("/")
#         first_report_station = trip.dutyperiods[0].flights[0].departure_station
#         first_report_tz = ZoneInfo(airports[first_report_station].tz)
#         first_report = complete_future_time(start, future=first_report_lcl, strf=TIME)
#         first_report = first_report.replace(tzinfo=first_report_tz)
#         assert trip.footer is not None
#         expanded = Trip(
#             number=trip.header.number,
#             positions=trip.header.positions,
#             operations=trip.header.operations,
#             special_qualifications=bool(trip.header.special_qualification),
#             block=parse_duration(trip.footer.block),
#             synth=parse_duration(trip.footer.synth),
#             total_pay=parse_duration(trip.footer.total_pay),
#             tafb=parse_duration(trip.footer.tafb),
#             dutyperiods=expand_dutyperiods(trip.dutyperiods, first_report, airports),
#             # source_ref=trip.s,
#         )
#         trips.append(expanded)
#     return trips


# def expand_dutyperiods(
#     dutyperiods: list[raw_lines.DutyPeriod],
#     first_report: datetime,
#     airports: dict[str, Airport],
# ):

#     expanded: list[DutyPeriod] = []
#     current_report: datetime | None = first_report
#     for dutyperiod in dutyperiods:
#         # FIXME do different error checking here
#         assert current_report is not None, (
#             "current_report is None, but there are still dutyperiods "
#             "remaining. This is probably due to a missing layover odl"
#         )
#         expanded_dp = expand_dutyperiod(dutyperiod, current_report, airports)
#         expanded.append(expanded_dp)
#         current_report = None
#         if expanded_dp.layover is not None:
#             current_report = expanded_dp.release + expanded_dp.layover.odl
#     return expanded


# def expand_dutyperiod(
#     dutyperiod: raw_lines.DutyPeriod,
#     report: datetime,
#     airports: dict[str, Airport],
# ) -> DutyPeriod:
#     idx = int(dutyperiod.flights[0].dutyperiod_idx)
#     assert dutyperiod.release is not None
#     release_lcl, _ = dutyperiod.release.release.split("/")
#     release_station = dutyperiod.flights[-1].arrival_station
#     release_tz = ZoneInfo(airports[release_station].tz)
#     release_time = complete_future_time(
#         report, release_lcl, tz_info=release_tz, strf=TIME
#     )

#     return DutyPeriod(
#         idx=idx,
#         report=report,
#         report_station=dutyperiod.flights[0].departure_station,
#         release=release_time,
#         release_station=release_station,
#         block=parse_duration(dutyperiod.release.block),
#         synth=parse_duration(dutyperiod.release.synth),
#         total_pay=parse_duration(dutyperiod.release.total_pay),
#         duty=parse_duration(dutyperiod.release.duty),
#         flight_duty=parse_duration(dutyperiod.release.flight_duty),
#         flights=expand_flights(dutyperiod.flights, report, airports),
#         layover=expand_layover(layover=dutyperiod.layover),
#     )


# def expand_flights(
#     flights: list[raw_lines.Flight], ref_date: datetime, airports: dict[str, Airport]
# ) -> list[Flight]:
#     expanded: list[Flight] = []
#     current_ref = ref_date
#     for idx, flight in enumerate(flights, start=1):
#         expanded_flight = expand_flight(
#             flight=flight, idx=idx, ref_datetime=current_ref, airports=airports
#         )
#         current_ref = expanded_flight.arrival_time
#         expanded.append(expanded_flight)
#     return expanded


# def expand_flight(
#     flight: raw_lines.Flight,
#     idx: int,
#     ref_datetime: datetime,
#     airports: dict[str, Airport],
# ) -> Flight:
#     depart_lcl, _ = flight.departure_time.split("/")
#     departure_tz = ZoneInfo(airports[flight.departure_station].tz)
#     arrival_lcl, _ = flight.arrival_time.split("/")
#     arrival_tz = ZoneInfo(airports[flight.arrival_station].tz)
#     departure_time = complete_future_time(
#         ref_datetime, depart_lcl, tz_info=departure_tz, strf=TIME
#     )
#     arrival_time = complete_future_time(
#         departure_time, arrival_lcl, tz_info=arrival_tz, strf=TIME
#     )
#     return Flight(
#         dutyperiod_idx=int(flight.dutyperiod_idx),
#         idx=idx,
#         dep_arr_day=flight.dep_arr_day,
#         eq_code=flight.eq_code,
#         number=flight.flight_number,
#         deadhead=bool(flight.deadhead),
#         departure_station=flight.departure_station,
#         departure_time=departure_time,
#         meal=flight.meal,
#         arrival_station=flight.arrival_station,
#         arrival_time=arrival_time,
#         block=parse_duration(flight.block),
#         synth=parse_duration(flight.synth),
#         ground=parse_duration(flight.ground),
#         equipment_change=bool(flight.equipment_change),
#     )


# def expand_layover(layover: raw_lines.Layover | None) -> Layover | None:
#     if layover is None:
#         return layover
#     return Layover(
#         odl=parse_duration(layover.hotel.rest),
#         city=layover.hotel.layover_city,
#         hotel=expand_hotel(layover.hotel),
#         transportation=expand_transportation(layover.transportation),
#         hotel_additional=expand_hotel(layover.hotel_additional),
#         transportation_additional=expand_transportation(
#             layover.transportation_additional
#         ),
#     )


# def expand_hotel(
#     hotel: raw_lines.Hotel | raw_lines.HotelAdditional | None,
# ) -> Hotel | None:
#     if hotel is None:
#         return hotel
#     return Hotel(name=hotel.name, phone=hotel.phone)


# def expand_transportation(
#     trans: raw_lines.Transportation | raw_lines.TransportationAdditional | None,
# ) -> Transportation | None:
#     if trans is None:
#         return None
#     return Transportation(name=trans.name, phone=trans.phone)


# def parse_duration(dur_str: str) -> timedelta:
#     delta = regex_parse_duration(DURATION_PATTERN, dur_str).to_timedelta()
#     return delta


# def parse_time(time_str: str) -> time.struct_time:
#     struct = time.strptime(time_str, TIME)
#     return struct


# def assign_timezone(
#     iata: str, date_value: datetime, airports: dict[str, Airport]
# ) -> datetime:
#     new_tz = airports[iata].tz
#     tz_info = ZoneInfo(new_tz)
#     tz_aware_datetime = date_value.replace(tzinfo=tz_info)
#     return tz_aware_datetime


# def get_calendar_entries(trip: raw_lines.Trip) -> list[str]:
#     """Make a list of the calendar entries for this trip."""
#     calendar_strings: list[str] = []
#     for dutyperiod in trip.dutyperiods:
#         calendar_strings.append(dutyperiod.report.calendar)
#         for flight in dutyperiod.flights:
#             calendar_strings.append(flight.calendar)
#         assert dutyperiod.release is not None
#         calendar_strings.append(dutyperiod.release.calendar)
#         if dutyperiod.layover:
#             if dutyperiod.layover.hotel:
#                 calendar_strings.append(dutyperiod.layover.hotel.calendar)
#             if dutyperiod.layover.transportation:
#                 calendar_strings.append(dutyperiod.layover.transportation.calendar)
#             if dutyperiod.layover.hotel_additional:
#                 calendar_strings.append(dutyperiod.layover.hotel_additional.calendar)
#             if dutyperiod.layover.transportation_additional:
#                 calendar_strings.append(
#                     dutyperiod.layover.transportation_additional.calendar
#                 )
#     assert trip.footer is not None
#     calendar_strings.append(trip.footer.calendar)
#     calendar_entries: list[str] = []
#     for entry in calendar_strings:
#         calendar_entries.extend(entry.split())
#     return calendar_entries


# def get_start_dates(
#     from_date: datetime, to_date: datetime, calendar_entries: list[str]
# ) -> list[datetime]:
#     """Builds a list of no-tz YMD datetime representing start dates for trips."""
#     days = int((to_date - from_date) / timedelta(days=1)) + 1
#     # FIXME move validation tests outside function
#     # if days != len(calendar_entries):
#     #     raise ValueError(
#     #         f"{days} days in range, but {len(calendar_entries)} entries "
#     #         f"in calendar for trip {self!r}."
#     #     )
#     indexed_days = list(index_numeric_strings(calendar_entries))
#     # if len(indexed_days) != int(self.header.ops_count):
#     #     raise ValueError(
#     #         f"Expected {self.header.ops_count} dates, but found {indexed_days} in calendar {calendar_entries}"
#     #     )
#     start_dates: list[datetime] = []
#     for indexed in indexed_days:
#         start_date = from_date + timedelta(days=indexed.idx)
#         # if start_date.day != int(indexed.txt):
#         #     raise ValueError(
#         #         f"Error building date. start_date: {from_date}, "
#         #         f"day: {indexed.txt}, calendar_entries:{calendar_entries!r}"
#         #     )
#         start_dates.append(start_date)
#     # print(f"Trip: {self.number()}, start dates: {start_dates}")
#     return start_dates


# def get_from_to(effective: datetime, calendar_range: str) -> tuple[datetime, datetime]:
#     # if self.page_header_2 is None:
#     #     raise ValueError("Tried to get from_to but page_header_2 was None.")
#     # effective = self.effective()
#     # TODO refactor this function after from to added to parser.
#     from_md = calendar_range[:5]
#     to_md = calendar_range[6:]
#     from_date = complete_future_mdt(effective, from_md, strf=MONTH_DAY)
#     to_date = complete_future_mdt(effective, to_md, strf=MONTH_DAY)
#     return from_date, to_date
