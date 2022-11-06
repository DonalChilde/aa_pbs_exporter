####################################################
#                                                  #
# src/snippets/datetime/datetime_from_struct_time.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-02T07:58:50-07:00            #
# Last Modified: 2022-11-06T07:30:52-07:00         #
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
    if tz_info is None:
        tz_info = ZoneInfo(struct.tm_zone)
    return datetime(year, month, day, hour, minute, second, tzinfo=tz_info)
