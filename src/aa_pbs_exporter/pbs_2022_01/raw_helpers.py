from typing import Sequence, Tuple

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.snippets.indexed_string.filters import is_numeric
from aa_pbs_exporter.snippets.indexed_string.index_and_filter_strings import (
    index_and_filter_strings,
)


def collect_start_days(calendar_entries: Sequence[str]) -> list[Tuple[int, int]]:
    indexed_days = list(
        index_and_filter_strings(strings=calendar_entries, string_filter=is_numeric)
    )
    return [(x.idx, int(x.txt)) for x in indexed_days]


def collect_calendar_entries(trip: raw.Trip) -> list[str]:
    """Make a list of the calendar entries for this trip."""
    calendar_strings: list[str] = []
    for dutyperiod in trip.dutyperiods:
        calendar_strings.append(dutyperiod.report.calendar)
        for flight in dutyperiod.flights:
            calendar_strings.append(flight.calendar)
        assert dutyperiod.release is not None
        calendar_strings.append(dutyperiod.release.calendar)
        if dutyperiod.layover:
            if dutyperiod.layover.hotel:
                calendar_strings.append(dutyperiod.layover.hotel.calendar)
            if dutyperiod.layover.transportation:
                calendar_strings.append(dutyperiod.layover.transportation.calendar)
            if dutyperiod.layover.hotel_additional:
                calendar_strings.append(dutyperiod.layover.hotel_additional.calendar)
            if dutyperiod.layover.transportation_additional:
                calendar_strings.append(
                    dutyperiod.layover.transportation_additional.calendar
                )
    assert trip.footer is not None
    calendar_strings.append(trip.footer.calendar)
    if trip.calendar_only:
        calendar_strings.append(trip.calendar_only.calendar)
    calendar_entries: list[str] = []
    for entry in calendar_strings:
        calendar_entries.extend(entry.split())
    return calendar_entries
