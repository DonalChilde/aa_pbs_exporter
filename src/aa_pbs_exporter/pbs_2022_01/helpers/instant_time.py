from dataclasses import dataclass
from datetime import date, datetime, time, UTC
from typing import Callable, Generic, Protocol, TypedDict, TypeVar

T = TypeVar("T", bound="InstantProtocol")
T2 = TypeVar("T2", bound="InstantDateProtocol")
T3 = TypeVar("T3", bound="InstantTimeProtocol")

# TODO add to snippets
# The purposeof this code is to store a tz name with a date time value.
# Mostly with an eye towards serialization, and easy manipulation.


class InstantTimeDict(TypedDict):
    time: time
    tz_name: str


@dataclass
class InstantTime:
    time: time
    tz_name: str


class InstantTimeProtocol(Protocol):
    time: time
    tz_name: str


class InstantDateDict(TypedDict):
    date: date
    tz_name: str


@dataclass
class InstantDate:
    date: date
    tz_name: str


class InstantDateProtocol(Protocol):
    date: date
    tz_name: str


class InstantDict(TypedDict):
    utc_datetime: datetime
    tz_name: str


@dataclass
class Instant:
    utc_datetime: datetime
    tz_name: str


class InstantProtocol(Protocol):
    utc_datetime: datetime
    tz_name: str


def instant_factory(value: datetime, tz_name: str) -> Instant:
    if value.tzinfo is None:
        raise ValueError(f"Instant factory received a naive datetime: {value!r}")
    if value.tzinfo != UTC:
        raise ValueError(
            f"Instant factory received an aware datetime that was not UTC: {value!r}"
        )
    return Instant(utc_datetime=value, tz_name=tz_name)


class InstantUtil(Generic[T]):
    def __init__(self, factory: Callable[[datetime, str], T]) -> None:
        self.factory = factory

    def to_dict(self, value: T) -> InstantDict:
        return {"utc_datetime": value.utc_datetime, "tz_name": value.tz_name}

    def from_dict(self, value: InstantDict) -> T:
        return self.factory(value["utc_datetime"], value["tz_name"])


class InstantTimeUtil(Generic[T3]):
    def __init__(self, factory: Callable[[time, str], T3]) -> None:
        self.factory = factory

    def to_dict(self, value: T3) -> InstantTimeDict:
        return {"time": value.time, "tz_name": value.tz_name}

    def from_dict(self, value: InstantTimeDict) -> T3:
        return self.factory(value["time"], value["tz_name"])


class InstantDateUtil(Generic[T2]):
    def __init__(self, factory: Callable[[date, str], T2]) -> None:
        self.factory = factory

    def to_dict(self, value: T2) -> InstantDateDict:
        return {"date": value.date, "tz_name": value.tz_name}

    def from_dict(self, value: InstantDateDict) -> T2:
        return self.factory(value["date"], value["tz_name"])
