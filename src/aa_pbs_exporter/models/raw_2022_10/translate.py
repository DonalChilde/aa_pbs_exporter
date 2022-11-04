from datetime import date, datetime, timedelta
import time
from typing import Sequence
from zoneinfo import ZoneInfo

from aa_pbs_exporter.airports.airport_model import Airport
from aa_pbs_exporter.airports.airports import by_iata
from aa_pbs_exporter.models import bid_package_2022_10 as aa
from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.models.raw_2022_10 import raw_lines

# from aa_pbs_exporter.util.complete_partial_datetime import complete_future_mdt
from aa_pbs_exporter.util.index_numeric_strings import index_numeric_strings


def translate_package(bid_package: raw.Package, source: str) -> aa.BidPackage:
    airports: dict[str, Airport] = {}
    for iata in bid_package.collect_iata_codes():
        airports[iata] = by_iata(iata)
    bid_package.resolve_package_dates(airports=airports)
    from_date, to_date = bid_package.from_to()
    aa_trips: list[aa.Trip] = []
    for page in bid_package.pages:
        aa_trips.extend(translate_pages(page=page))
    return aa.BidPackage(
        source=source,
        base=bid_package.base(),
        satelite_bases=bid_package.satelite_bases(),
        from_date=from_date,
        to_date=to_date,
        trips=aa_trips,
        airports=airports,
    )


def translate_pages(page: raw.Page) -> list[aa.Trip]:
    aa_trips: list[aa.Trip] = []
    for trip in page.trips:
        for resolved_start_date in trip.resolved_start_dates:
            aa_trip = aa.Trip(
                number=trip.number(),
                base=trip.base(page=page),
                satelite_base=trip.satelite_base(page=page),
                positions=trip.positions(),
                operations=trip.operations(),
                division=trip.division(),
                equipment=trip.equipment(),
                special_qualifications=trip.special_qualification(),
                block=trip.block(),
                synth=trip.synth(),
                total_pay=trip.pay(),
                tafb=trip.tafb(),
                dutyperiods=translate_dutyperiods(
                    resolved_start_date=resolved_start_date, trip=trip
                ),
            )
            aa_trips.append(aa_trip)
    return aa_trips


# def translate_trip_starts(
#     start_dates: Sequence[datetime],
#     trip: raw.Trip,
#     airports: dict[str, Airport],
#     footer: raw_lines.PageFooter,
# ) -> list[aa.Trip]:
#     aa_trips: list[aa.Trip] = []
#     for start_date in start_dates:
#         first_departure_airport = trip.dutyperiods[0].flights[0].departure_station
#         resolved_first_report = resolve_start_date(
#             start_date=start_date,
#             first_report=trip.dutyperiods[0].report.report,
#             tz_string=airports[first_departure_airport].tz,
#         )
#         aa_trip = aa.Trip(
#             number=trip.header.number,
#             base=footer.base,
#             satelite_base=footer.satelite_base,
#             positions=trip.header.positions,
#             operations=trip.header.operations,
#             division=footer.division,
#             equipment=footer.equipment,
#             special_qualifications=bool(trip.header.special_qualification),
#             block=parse_duration(trip.footer.block),
#             synth=parse_duration(trip.footer.synth),
#             total_pay=parse_duration(trip.footer.total_pay),
#             tafb=parse_duration(trip.footer.tafb),
#             dutyperiods=translate_dutyperiods(
#                 resolved_first_report=resolved_first_report,
#                 dutyperiods=trip.dutyperiods,
#                 airports=airports,
#             ),
#         )
#         aa_trips.append(aa_trip)
#     return aa_trips


def translate_dutyperiods(
    resolved_start_date: datetime,
    trip: raw.Trip,
) -> list[aa.DutyPeriod]:
    aa_dutyperiods: list[aa.DutyPeriod] = []
    for idx, dutyperiod in enumerate(trip.dutyperiods):
        aa_dutyperiod = aa.DutyPeriod(
            idx=idx,
            report=dutyperiod.resolved_reports[resolved_start_date].report,
            report_station=dutyperiod.report_station(),
            release=dutyperiod.resolved_reports[resolved_start_date].release,
            release_station=dutyperiod.release_station(),
            block=dutyperiod.block(),
            synth=dutyperiod.synth(),
            total_pay=dutyperiod.pay(),
            duty=dutyperiod.duty(),
            flight_duty=dutyperiod.flight_duty(),
            flights=translate_flights(
                resolved_start_date=resolved_start_date, dutyperiod=dutyperiod
            ),
            layover=translate_layover(layover=dutyperiod.layover),
        )
        aa_dutyperiods.append(aa_dutyperiod)
    return aa_dutyperiods


def translate_layover(layover: raw.Layover) -> aa.Layover:
    if layover is None:
        return None
    if layover.hotel_name():
        if layover.transportation_name():
            aa_transportation = aa.Transportation(
                name=layover.transportation_name(), phone=layover.transportation_phone()
            )
        else:
            aa_transportation = None
        aa_hotel = aa.Hotel(
            name=layover.hotel_name(),
            phone=layover.hotel_phone(),
            transportation=aa_transportation,
        )
    else:
        aa_hotel = None
    if layover.hotel_additional_name():
        if layover.transportation_additional_name():
            aa_add_transportation = aa.Transportation(
                name=layover.transportation_additional_name(),
                phone=layover.transportation_additional_phone(),
            )
        else:
            aa_add_transportation = None
        aa_add_hotel = aa.Hotel(
            name=layover.hotel_additional_name(),
            phone=layover.hotel_additional_phone(),
            transportation=aa_add_transportation,
        )
    else:
        aa_add_hotel = None
    layover = aa.Layover(
        odl=layover.rest(),
        city=layover.city(),
        hotel=aa_hotel,
        additional_hotel=aa_add_hotel,
    )
    return layover


# def release_and_next_report(
#     report: datetime, dutyperiod: raw.DutyPeriod, airports: dict[str, Airport]
# ) -> tuple[datetime, datetime | None]:
#     duty = parse_duration(dutyperiod.release.duty)
#     release = report + duty
#     tz_str = airports[dutyperiod.flights[-1].arrival_station].tz
#     arrival_tz = ZoneInfo(tz_str)
#     release = release.astimezone(arrival_tz)
#     if dutyperiod.hotel is not None:
#         next_report = release + parse_duration(dutyperiod.hotel.rest)
#         return release, next_report
#     return release, None


def translate_flights(
    resolved_start_date: datetime,
    dutyperiod: raw.DutyPeriod,
) -> list[aa.Flight]:
    aa_flights: list[aa.Flight] = []
    for idx, flight in enumerate(dutyperiod.flights):
        aa_flight = aa.Flight(
            dutyperiod_index=flight.dp_idx(),
            idx=idx + 1,
            d_a=flight.d_a(),
            eq_code=flight.eq_code(),
            number=flight.number(),
            deadhead=flight.deadhead(),
            departure_station=flight.departure_station(),
            departure_time=flight.resolved_flights[resolved_start_date].departure,
            meal=flight.meal(),
            arrival_station=flight.arrival_station(),
            arrival_time=flight.resolved_flights[resolved_start_date].arrival,
            block=flight.block(),
            synth=flight.synth(),
            ground=flight.ground(),
            equipment_change=flight.equipment_change(),
        )
        aa_flights.append(aa_flight)
    return aa_flights


# def resolve_start_date(
#     start_date: datetime, first_report: str, tz_string: str
# ) -> datetime:
#     tz_info = ZoneInfo(tz_string)
#     local, hbt = first_report.split("/")
#     struct = time.strptime(local, "%H%M")
#     start_date = start_date.replace(
#         tzinfo=tz_info, hour=struct.tm_hour, minute=struct.tm_min
#     )
#     return start_date


def dutyperiod_report_release(
    start_date: datetime, dutyperiod: raw.DutyPeriod, airports: dict[str, Airport]
) -> tuple[datetime, datetime]:
    raise NotImplementedError


def flight_departure_arrival(
    start_date: datetime, flight: raw_lines.Flight, airports: dict[str, Airport]
) -> tuple[datetime, datetime]:
    raise NotImplementedError


# def collect_airports(bid_package: raw.Package) -> dict[str, Airport]:
#     iatas: set[str] = set()
#     for page in bid_package.pages:
#         iatas.add(page.page_footer.base)
#         iatas.add(page.page_footer.satelite_base)
#         for trip in page.trips:
#             for dutyperiod in trip.dutyperiods:
#                 for flight in dutyperiod.flights:
#                     iatas.add(flight.departure_station)
#                     iatas.add(flight.arrival_station)
#     if None in iatas:
#         iatas.remove(None)  # type: ignore
#     if "" in iatas:
#         iatas.remove("")
#     airports: dict[str, Airport] = {}
#     for iata in iatas:
#         airports[iata] = by_iata(iata)
#     return airports


# def extract_start_dates(
#     trip: raw.Trip, effective: datetime, from_to: str
# ) -> Sequence[datetime]:
#     calendar_entries = extract_calendar_entries(trip)
#     from_date, to_date = expand_from_to(effective, from_to)
#     days = days_in_range(from_date, to_date)
#     if days != len(calendar_entries):
#         raise ValueError(
#             f"{days} days in range, but {len(calendar_entries)} entries in calendar."
#         )
#     indexed_days = list(index_numeric_strings(calendar_entries))
#     start_dates: list[datetime] = []
#     for idx in indexed_days:
#         start_date = from_date + timedelta(days=idx.idx)
#         if start_date.day != int(idx.str_value):
#             raise ValueError(
#                 f"Error building date. start_date: {from_date}, "
#                 f"day: {idx.str_value}, calendar_entries:{calendar_entries!r}"
#             )
#         start_dates.append(start_date)
#     return start_dates


# def days_in_range(from_date: date, to_date: date) -> int:
#     delta = to_date - from_date
#     return int(delta / timedelta(days=1)) + 1


# def expand_from_to(effective: datetime, from_to: str) -> tuple[datetime, datetime]:
#     from_md = from_to[:5]
#     to_md = from_to[6:]
#     strf = "%m/%d"
#     from_date = complete_future_mdt(effective, from_md, strf=strf)
#     to_date = complete_future_mdt(effective, to_md, strf=strf)
#     return from_date, to_date


# def extract_calendar_entries(trip: raw.Trip) -> list[str]:
#     calendar_strings: list[str] = []
#     for dutyperiod in trip.dutyperiods:
#         calendar_strings.append(dutyperiod.report.calendar)
#         for flight in dutyperiod.flights:
#             calendar_strings.append(flight.calendar)
#         calendar_strings.append(dutyperiod.release.calendar)
#         if dutyperiod.hotel:
#             calendar_strings.append(dutyperiod.hotel.calendar)
#         if dutyperiod.transportation:
#             calendar_strings.append(dutyperiod.transportation.calendar)
#         if dutyperiod.hotel_additional:
#             calendar_strings.append(dutyperiod.hotel_additional.calendar)
#         if dutyperiod.transportation_additional:
#             calendar_strings.append(dutyperiod.transportation_additional.calendar)
#     calendar_strings.append(trip.footer.calendar)
#     calendar_entries: list[str] = []
#     for entry in calendar_strings:
#         calendar_entries.extend(entry.split())
# return calendar_entries
