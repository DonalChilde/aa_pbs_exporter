from aa_pbs_exporter.pbs_2022_01.models import raw


def collect_calendar_entries(trip: raw.Trip) -> list[str]:
    """Make a list of the calendar entries for this trip."""
    calendar_entries: list[str] = []
    for dutyperiod in trip.dutyperiods:
        calendar_entries.extend(dutyperiod.report.calendar)
        for flight in dutyperiod.flights:
            calendar_entries.extend(flight.calendar)
        assert dutyperiod.release is not None
        calendar_entries.extend(dutyperiod.release.calendar)
        if dutyperiod.layover:
            for info in dutyperiod.layover.hotel_info:
                if info.hotel is not None:
                    calendar_entries.extend(info.hotel.calendar)
                if info.transportation is not None:
                    calendar_entries.extend(info.transportation.calendar)

    assert trip.footer is not None
    calendar_entries.extend(trip.footer.calendar)
    if trip.calendar_only:
        calendar_entries.extend(trip.calendar_only.calendar)
    return calendar_entries
