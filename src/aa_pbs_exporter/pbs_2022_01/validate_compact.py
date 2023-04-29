from datetime import date
from typing import Sequence, Tuple
from uuid import UUID

from aa_pbs_exporter.pbs_2022_01.models import compact, raw
from aa_pbs_exporter.pbs_2022_01.validation_helper import send_validation_message
from aa_pbs_exporter.snippets.messages.message import Message


def validate_trip(raw_trip: raw.Trip, compact_trip: compact.Trip, ctx: dict | None):
    pass


# pass in temp variables like len(date_range) via ctx
# compact model is validated just before returning created objects.


def validate_start_date(day: Tuple[int, int], start_date: date, uuid: UUID):
    if day[1] != start_date.day:
        msg = Message(
            f"Partial date: {day!r} does not match day of date: {start_date.isoformat()}. uuid:{uuid}"
        )
        send_validation_message(msg=msg, ctx=None)


def validate_calendar_entry_count(
    calendar_entries: Sequence[str], valid_dates: Sequence[date], uuid: UUID
):
    if not len(calendar_entries) == len(valid_dates):
        msg = Message(
            f"Count of calendar_entries: {len(calendar_entries)} does not match valid_dates: {len(valid_dates)}. uuid: {uuid}"
        )
        send_validation_message(msg=msg, ctx=None)
    return
