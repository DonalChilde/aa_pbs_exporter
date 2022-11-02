from datetime import date, datetime, timedelta
from typing import Iterator, Sequence

from aa_pbs_exporter.models import bid_package_2022_10 as aa
from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.util.complete_partial_datetime import complete_future_mdt
from aa_pbs_exporter.util.index_numeric_strings import index_numeric_strings


def extract_start_dates(
    trip: raw.Trip, effective: datetime, from_to: str
) -> Sequence[date]:
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
