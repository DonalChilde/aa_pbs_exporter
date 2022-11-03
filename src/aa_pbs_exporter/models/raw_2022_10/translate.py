from datetime import date, datetime, timedelta
from typing import Sequence
from zoneinfo import ZoneInfo

from aa_pbs_exporter.airports.airport_model import Airport
from aa_pbs_exporter.airports.airports import by_iata
from aa_pbs_exporter.models import bid_package_2022_10 as aa
from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.models.raw_2022_10 import raw_lines
from aa_pbs_exporter.util.complete_partial_datetime import complete_future_mdt
from aa_pbs_exporter.util.index_numeric_strings import index_numeric_strings


def translate_package(bid_package: raw.Package, source: str) -> aa.BidPackage:
    base = bid_package.pages[0].page_footer.base
    effective = bid_package.pages[0].effective
    from_to = bid_package.pages[0].from_to
    start, end = expand_from_to(effective=effective, from_to=from_to)
    aa_trips: list[aa.Trip] = []
    airports = collect_airports(bid_package=bid_package)
    for page in bid_package.pages:
        parsed_trips = translate_pages(page=page, airports=airports)
        aa_trips.extend(parsed_trips)
    return aa.BidPackage(
        source=source,
        base=base,
        start=start,
        end=end,
        trips=aa_trips,
        airports=airports,
    )


def translate_pages(page: raw.Page, airports: dict[str, Airport]) -> list[aa.Trip]:
    aa_trips: list[aa.Trip] = []
    effective = page.effective()
    from_to = page.from_to()
    for trip in page.trips:
        start_dates = extract_start_dates(trip, effective, from_to)
        if len(start_dates) != int(trip.header.ops_count):
            raise ValueError(
                f"start date count {len(start_dates)} did not match "
                f"ops count {trip.header.ops_count} for trip {trip}"
            )
        aa_trip_starts = translate_trip_starts(
            start_dates, trip, airports, page.page_footer
        )
        aa_trips.extend(aa_trip_starts)
    return aa_trips


def translate_trip_starts(
    start_dates: Sequence[datetime],
    trip: raw.Trip,
    airports: dict[str, Airport],
    footer: raw_lines.PageFooter,
) -> list[aa.Trip]:
    aa_trips: list[aa.Trip] = []
    for start_date in start_dates:
        resolved_first_report = resolve_start_date(
            start_date=start_date,
            first_report=trip.dutyperiods[0].report.report,
            tz_string=airports[trip.dutyperiods[0].flights[0].departure_station],
        )
        aa_trip = aa.Trip(
            number=trip.header.number,
            base=footer.base,
            satelite_base=footer.satelite_base,
            positions=trip.header.positions,
            operations=trip.header.operations,
            division=footer.division,
            equipment=footer.equipment,
            special_qualifications=bool(trip.header.special_qualification),
            block=parse_duration(trip.footer.block),
            synth=parse_duration(trip.footer.synth),
            total_pay=parse_duration(trip.footer.total_pay),
            tafb=parse_duration(trip.footer.tafb),
            dutyperiods=translate_dutyperiods(
                resolved_first_report=resolved_first_report,
                dutyperiods=trip.dutyperiods,
                airports=airports,
            ),
        )
        aa_trips.append(aa_trip)
    return aa_trips


def translate_dutyperiods(
    resolved_first_report: datetime,
    dutyperiods: list[raw.DutyPeriod],
    airports: dict[str, Airport],
) -> list[aa.DutyPeriod]:
    aa_dutyperiods: list[aa.DutyPeriod] = []
    ref_time: datetime | None = resolved_first_report
    for idx, dutyperiod in enumerate(dutyperiods):
        if ref_time is None:
            raise ValueError(
                f"{ref_time=!r}, but there are remaining "
                f"raw dutyperiods {dutyperiods!r}"
            )
        release, next_report = release_and_next_report(
            report=ref_time, dutyperiod=dutyperiod, airports=airports
        )
        aa_dutyperiod = aa.DutyPeriod(
            idx=idx + 1,
            report=ref_time,
            report_station=dutyperiod.flights[0].departure_station,
            release=release,
            release_station=dutyperiod.flights[-1].arrival_station,
            block=parse_duration(dutyperiod.release.block),
            synth=parse_duration(dutyperiod.release.synth),
            total_pay=parse_duration(dutyperiod.release.total_pay),
            duty=parse_duration(dutyperiod.release.duty),
            flight_duty=parse_duration(dutyperiod.release.flight_duty),
            flights=translate_flights(
                report=ref_time,
                dp_idx=idx + 1,
                flights=dutyperiod.flights,
                airports=airports,
            ),
            layover=make_layover(dutyperiod),
        )
        ref_time = next_report
        aa_dutyperiods.append(aa_dutyperiod)
    return aa_dutyperiods


def make_layover(dutyperiod: raw.DutyPeriod) -> aa.Layover:
    raise NotImplementedError


def release_and_next_report(
    report: datetime, dutyperiod: raw.DutyPeriod, airports: dict[str, Airport]
) -> tuple[datetime, datetime | None]:
    duty = parse_duration(dutyperiod.release.duty)
    release = report + duty
    tz_str = airports[dutyperiod.flights[-1].arrival_station].tz
    arrival_tz = ZoneInfo(tz_str)
    release = release.astimezone(arrival_tz)
    if dutyperiod.hotel is not None:
        next_report = release + parse_duration(dutyperiod.hotel.rest)
        return release, next_report
    return release, None


def translate_flights(
    report: datetime,
    dp_idx: int,
    flights: list[raw_lines.Flight],
    airports: dict[str, Airport],
) -> list[aa.Flight]:
    aa_flights: list[aa.Flight] = []
    ref_time = report
    for idx, flight in enumerate(flights):
        departure, arrival = flight_departure_arrival(
            start_date=ref_time, flight=flight, airports=airports
        )
        aa_flight = aa.Flight(
            dutyperiod_index=dp_idx,
            idx=idx + 1,
            d_a=flight.d_a,
            eq_code=flight.eq_code,
            number=flight.flight_number,
            deadhead=bool(flight.deadhead),
            departure_station=flight.departure_station,
            departure_time=departure,
            meal=flight.meal,
            arrival_station=flight.arrival_station,
            arrival_time=flight.arrival_time,
            block=parse_duration(flight.block),
            synth=parse_duration(flight.synth),
            ground=parse_duration(flight.ground),
            equipment_change=bool(flight.equipment_change),
        )
        aa_flights.append(aa_flight)
        ref_time = arrival
    return aa_flights


def parse_duration(dur_str: str) -> timedelta:
    raise NotImplementedError


def resolve_start_date(
    start_date: datetime, first_report: str, tz_string: str
) -> datetime:
    raise NotImplementedError


def dutyperiod_report_release(
    start_date: datetime, dutyperiod: raw.DutyPeriod, airports: dict[str, Airport]
) -> tuple[datetime, datetime]:
    raise NotImplementedError


def flight_departure_arrival(
    start_date: datetime, flight: raw_lines.Flight, airports: dict[str, Airport]
) -> tuple[datetime, datetime]:
    raise NotImplementedError


def collect_airports(bid_package: raw.Package) -> dict[str, Airport]:
    iatas: set[str] = set()
    for page in bid_package.pages:
        iatas.add(page.page_footer.base)
        iatas.add(page.page_footer.satelite_base)
        for trip in page.trips:
            for dutyperiod in trip.dutyperiods:
                for flight in dutyperiod.flights:
                    iatas.add(flight.departure_station)
                    iatas.add(flight.arrival_station)
    if None in iatas:
        iatas.remove(None)  # type: ignore
    if "" in iatas:
        iatas.remove("")
    airports = dict({iata: by_iata(iata) for iata in iatas})
    return airports


def extract_start_dates(
    trip: raw.Trip, effective: datetime, from_to: str
) -> Sequence[datetime]:
    calendar_entries = extract_calendar_entries(trip)
    from_date, to_date = expand_from_to(effective, from_to)
    days = days_in_range(from_date, to_date)
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


def days_in_range(from_date: date, to_date: date) -> int:
    delta = to_date - from_date
    return int(delta / timedelta(days=1)) + 1


def expand_from_to(effective: datetime, from_to: str) -> tuple[datetime, datetime]:
    from_md = from_to[:5]
    to_md = from_to[6:]
    strf = "%m/%d"
    from_date = complete_future_mdt(effective, from_md, strf=strf)
    to_date = complete_future_mdt(effective, to_md, strf=strf)
    return from_date, to_date


def extract_calendar_entries(trip: raw.Trip) -> list[str]:
    calendar_strings: list[str] = []
    for dutyperiod in trip.dutyperiods:
        calendar_strings.append(dutyperiod.report.calendar)
        for flight in dutyperiod.flights:
            calendar_strings.append(flight.calendar)
        calendar_strings.append(dutyperiod.release.calendar)
        if dutyperiod.hotel:
            calendar_strings.append(dutyperiod.hotel.calendar)
        if dutyperiod.transportation:
            calendar_strings.append(dutyperiod.transportation.calendar)
        if dutyperiod.hotel_additional:
            calendar_strings.append(dutyperiod.hotel_additional.calendar)
        if dutyperiod.transportation_additional:
            calendar_strings.append(dutyperiod.transportation_additional.calendar)
    calendar_strings.append(trip.footer.calendar)
    calendar_entries: list[str] = []
    for entry in calendar_strings:
        calendar_entries.extend(entry.split())
    return calendar_entries
