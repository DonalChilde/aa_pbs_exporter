####################################################
#                                                  #
#    src/snippets/datetime/factored_duration.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-12-03T17:59:04-07:00            #
# Last Modified: 2022-12-04T01:00:32.152328+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from dataclasses import asdict, dataclass
from datetime import timedelta
from decimal import Decimal

SECONDS_IN_HOUR = 60 * 60
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR
SECONDS_IN_YEAR = 365 * SECONDS_IN_DAY
HOURS_IN_YEAR = 365 * 24


@dataclass(frozen=True)
class FactoredDuration:
    is_negative: bool = False
    years: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    fractional_seconds: int = 0
    # fractional_exponent should be => magnitude of fractional seconds
    fractional_exponent: int = 1

    def seconds_as_Decimal(self) -> Decimal:
        return Decimal(self.seconds_as_str())

    def seconds_as_str(self) -> str:
        return f"{self.seconds}.{self.fractional_seconds:0{self.fractional_exponent}}"

    def padded_fractional_seconds(self) -> str:
        return self.seconds_as_str().split(".")[1]

    def to_iso_format(self) -> str:
        """
        Get an iso string of the Duration.
        https://en.wikipedia.org/wiki/ISO_8601#Durations
        """

        return duration_to_iso(**asdict(self))

    @classmethod
    def from_iso(cls, iso_string: str) -> "FactoredDuration":
        """
        Make a Duration from an iso string.

        ISO Duration strings are ambiguous. This function assumes 365 days in a year,
        30 days in a month, 7 days in a week, 24 hours in a day, 60 minutes an hour,
        and 60 seconds in a minute. To allow greatest precision for fractional values,
        all fields will be converted to seconds before the fraction is applied.
        For example, 1 day = 86400 seconds. P.34D would be calulated as
        86400 * .34 = 29376 seconds. Duration(seconds = 29376)

        Args:
            iso_string: _description_

        Returns:
            _description_
        """
        raise NotImplementedError

    def to_timedelta(self) -> timedelta:
        return timedelta(
            days=(self.years * 365) + self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=float(self.seconds_as_Decimal()),
        )

    @classmethod
    def from_timedelta(cls, delta) -> "FactoredDuration":
        is_negative = bool(delta.days < 0)
        abs_delta = abs(delta)
        years, rem = divmod(abs_delta, timedelta(days=365))
        days, rem = divmod(rem, timedelta(days=1))
        hours, rem = divmod(rem, timedelta(hours=1))
        minutes, rem = divmod(rem, timedelta(minutes=1))
        seconds = int(rem.total_seconds())
        return FactoredDuration(
            is_negative=is_negative,
            years=years,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            fractional_seconds=rem.microseconds,
            fractional_exponent=6,
        )

    @classmethod
    def from_seconds(cls, seconds: float | Decimal | int) -> "FactoredDuration":
        # TODO rework to allow decimal, keep precision
        raise NotImplementedError

    @classmethod
    def from_nanoseconds(cls, nanos: int) -> "FactoredDuration":
        raise NotImplementedError


def duration_to_iso(
    is_negative: bool = False,
    years: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    fractional_seconds: int = 0,
    fractional_exponent: int = 0,
):
    if fractional_seconds:
        frac_str = f".{fractional_seconds:0{fractional_exponent}}"
    else:
        frac_str = ""
    return (
        f"{'-'if is_negative else ''}P{f'{years}Y' if years else '' }"
        f"{f'{days}D' if days else ''}T{f'{hours}H' if hours else ''}"
        f"{f'{minutes}M'if minutes else ''}"
        f"{f'{seconds:01d}{frac_str}S'if (seconds or frac_str)else''}"
    )


def duration_to_HHMMSS(
    is_negative: bool = False,
    years: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
    fractional_seconds: int = 0,
    fractional_exponent: int = 0,
    hm_separator: str = ":",
    ms_separator: str = ":",
    timespec=None,
) -> str:
    if fractional_seconds:
        frac_str = f".{fractional_seconds:0{fractional_exponent}}"
    else:
        frac_str = ""
    total_hours = (years * 365 * 24) + (days * 24) + hours
    if timespec == "M":
        return f"{'-' if is_negative else''}{total_hours}{hm_separator}{minutes:02d}"

    if fractional_seconds:
        frac_str = f".{fractional_seconds:0{fractional_exponent}}"
    else:
        frac_str = ""
    return (
        f"{'-' if is_negative else''}{total_hours}{hm_separator}{minutes:02d}"
        f"{ms_separator}{seconds:02d}{frac_str}"
    )
