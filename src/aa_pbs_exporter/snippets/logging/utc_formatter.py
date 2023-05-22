####################################################
#                                                  #
#      src/snippets/logging/utc_formatter.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-30T09:47:59-07:00            #
# Last Modified: 2023-04-30T17:00:36.628111+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
from datetime import datetime, timezone
from typing import Any, Mapping


class UtcFormatter(logging.Formatter):
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
        dt = datetime.fromtimestamp(record.created, tz=timezone.utc)
        if datefmt == "iso" or datefmt is None:
            return dt.isoformat()
        return dt.strftime(datefmt)
