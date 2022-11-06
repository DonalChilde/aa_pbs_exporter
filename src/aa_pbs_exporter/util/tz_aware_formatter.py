####################################################
#                                                  #
#    src/snippets/logging/tz_aware_formatter.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-06T07:58:01-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
from datetime import timezone
from typing import Any, Mapping

from .datetime_from_struct_time import datetime_from_struct


class TZAwareFormatter(logging.Formatter):
    # default_time_format = "%Y"

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = "iso",
        style="%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        struct = self.converter(record.created)
        # logging.Record coerces to float:milliseconds
        # self.msecs = int((ct - int(ct)) * 1000) + 0.0  # see gh-89047
        micros = int(record.msecs) * 1000
        new_dt = datetime_from_struct(struct, microsecond=micros)
        if datefmt == "iso":
            dt_string = new_dt.isoformat()
        elif datefmt == "iso_utc":
            new_dt = new_dt.astimezone(timezone.utc)
            dt_string = new_dt.isoformat()
        elif datefmt:
            dt_string = new_dt.strftime(datefmt)
        else:
            dt_string = new_dt.strftime(self.default_time_format)
        return dt_string
