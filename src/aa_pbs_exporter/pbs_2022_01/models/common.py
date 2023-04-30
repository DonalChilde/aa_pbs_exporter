from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import BaseModel


class HashedFile(BaseModel):
    file_path: Path
    file_hash: str
    hash_method: str

    @classmethod
    def factory(cls, file_path: Path, file_hash: str, hash_method: str) -> "HashedFile":
        return cls(file_path=file_path, file_hash=file_hash, hash_method=hash_method)


class Instant(BaseModel):
    """Represents an instant in time.

    The datetime should be an aware datetime with a timezone of timezone.utc
    The tz_name field can store the local time zone name for conversions.
    Addition and subtraction of timedeltas is supported.
    Enforced use of utc time should prevent ambiguous math.
    """

    utc_date: datetime
    tz_name: str

    class Config:
        allow_mutation = False
        # frozen = True

    def local(self, tz_name: str | None = None) -> datetime:
        if tz_name is None:
            return self.utc_date.astimezone(tz=ZoneInfo(self.tz_name))
        return self.utc_date.astimezone(tz=ZoneInfo(tz_name))

    def new_tz(self, tz_name: str) -> "Instant":
        return Instant(utc_date=self.utc_date, tz_name=tz_name)

    def __copy__(self) -> "Instant":
        return Instant(utc_date=self.utc_date, tz_name=self.tz_name)

    def __add__(self, other: timedelta) -> "Instant":
        if not isinstance(other, timedelta):
            return NotImplemented
        new_instant = Instant(utc_date=self.utc_date + other, tz_name=self.tz_name)
        return new_instant

    def __sub__(self, other: timedelta) -> "Instant":
        if not isinstance(other, timedelta):
            return NotImplemented
        new_instant = Instant(utc_date=self.utc_date - other, tz_name=self.tz_name)
        return new_instant

    def __str__(self) -> str:
        return f"utc_date={self.utc_date.isoformat()}, tz_name={self.tz_name}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}("
            f"utc_date={self.utc_date!r}, tz_name={self.tz_name!r}"
            ")"
        )
