from datetime import date, datetime, timedelta
import time
from typing import Iterator, Sequence
from aa_pbs_exporter.models.raw_2022_10 import raw_bid_package as raw
from aa_pbs_exporter.models import bid_package_2022_10 as aa
from aa_pbs_exporter.util.complete_partial_datetime import complete_future_mdt

# TODO STOP! write the tests!


def extract_calendar(trip: raw.Trip, effective: date, from_to: str) -> Sequence[date]:
    calendar_entries = extract_calendar_entries(trip.dutyperiods)
    from_date, to_date = expand_from_to(effective, from_to)
    days = days_in_range(from_date, to_date)
    if days != len(calendar_entries):
        raise ValueError(
            f"{days} days in range, but {len(calendar_entries)} entries in calendar."
        )


def days_in_range(from_date: date, to_date: date) -> int:
    delta = to_date - from_date
    return int(delta / timedelta(days=1))


def expand_from_to(effective: date, from_to: str) -> tuple[date, date]:
    from_md = from_to[:5]
    to_md = from_to[6:]
    strf = "%m/%d"
    from_date = complete_future_mdt(effective, from_md, strf=strf)
    to_date = complete_future_mdt(effective, to_md, strf=strf)
    # parsed = datetime.strptime(f"{from_md}/{effective.year}", "%m/%d/%Y")
    # from_date = parsed.date()
    # parsed = datetime.strptime(f"{to_md}/{effective.year}", "%m/%d/%Y")
    # to_date = parsed.date()
    return from_date, to_date


def extract_calendar_entries(dutyperiods: Sequence[raw.DutyPeriod]) -> list[str]:
    calendar_strings: list[str] = []
    for dutyperiod in dutyperiods:
        calendar_strings.append(dutyperiod.report.calendar)
        for flight in dutyperiod.flights:
            calendar_strings.append(flight.calendar)
        calendar_strings.append(dutyperiod.release)
        calendar_strings.append(dutyperiod.hotel.calendar)
        calendar_strings.append(dutyperiod.transportation.calendar)
        calendar_strings.append(dutyperiod.hotel_additional.calendar)
        calendar_strings.append(dutyperiod.transportation_additional.calendar)
    calendar_entries: list[str] = []
    for entry in calendar_strings:
        calendar_entries.extend(entry.split())
    return calendar_entries
