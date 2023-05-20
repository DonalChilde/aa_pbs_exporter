from datetime import date
from time import struct_time


def complete_month_day(
    ref_date: date, struct: struct_time, future: bool = True
) -> date:
    """Get the next occurrance of a month and day."""
    # TODO add to snippets
    month = struct.tm_mon
    year = ref_date.year
    day = struct.tm_mday
    if future:
        if ref_date.month == month and ref_date.day > day:
            year += 1
        if ref_date.month > month:
            year += 1
    else:
        if ref_date.month == month and ref_date.day < day:
            year -= 1
        if ref_date.month < month:
            year -= 1
    return date(year, month, day)
