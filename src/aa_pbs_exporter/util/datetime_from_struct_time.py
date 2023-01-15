####################################################
#                                                  #
# src/snippets/datetime/datetime_from_struct_time.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-02T07:58:50-07:00            #
# Last Modified: 2022-12-04T00:56:52.171104+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from datetime import date, datetime, time, tzinfo
from time import struct_time
from zoneinfo import ZoneInfo


def date_from_struct(
    struct: struct_time,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
) -> date:
    if year is None:
        year = struct.tm_year
    if month is None:
        month = struct.tm_mon
    if day is None:
        day = struct.tm_mday
    return date(year, month, day)


def time_from_struct(
    struct: struct_time,
    hour: int | None = None,
    minute: int | None = None,
    second: int | None = None,
) -> time:
    if hour is None:
        hour = struct.tm_hour
    if minute is None:
        minute = struct.tm_min
    if second is None:
        second = struct.tm_sec
    return time(hour, minute, second)


def datetime_from_struct(
    struct: struct_time,
    *,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    hour: int | None = None,
    minute: int | None = None,
    second: int | None = None,
    microsecond: int | None = None,
    tz_info: tzinfo | None = None,
    aware: bool = True,
) -> datetime:
    if year is None:
        year = struct.tm_year
    if month is None:
        month = struct.tm_mon
    if day is None:
        day = struct.tm_mday
    if hour is None:
        hour = struct.tm_hour
    if minute is None:
        minute = struct.tm_min
    if second is None:
        second = struct.tm_sec
    if microsecond is None:
        microsecond = 0
    if aware:
        if tz_info is None:
            try:
                tz_info = ZoneInfo(struct.tm_zone)
            except Exception as error:
                raise ValueError(
                    f"Tried to make an aware datetime with {struct}, got {error}"
                ) from error
        return datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=tz_info
        )

    return datetime(year, month, day, hour, minute, second, microsecond, tzinfo=None)
