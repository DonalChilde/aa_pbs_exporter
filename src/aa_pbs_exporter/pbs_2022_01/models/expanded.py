"""


Assumptions:
    Trip.end = last Dutyperiod.release
    trip starts and ends in base
"""
import logging
from collections.abc import Generator
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from aa_pbs_exporter.pbs_2022_01.helpers.serialize_pydantic import SerializePydantic

from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile, Instant
from aa_pbs_exporter.snippets.timers import timers

logger = logging.getLogger(__name__)
time_logger = timers.TimeLogger(logger=logger, level=logging.INFO)


class Transportation(BaseModel):
    uuid: UUID
    name: str
    phone: str


class Hotel(BaseModel):
    uuid: UUID
    name: str
    phone: str


class HotelInfo(BaseModel):
    hotel: Hotel
    transportation: list[Transportation]


class Layover(BaseModel):
    uuid: UUID
    odl: timedelta
    city: str
    hotel_info: list[HotelInfo]


class Flight(BaseModel):
    uuid: UUID
    compact_uuid: UUID
    dp_idx: int
    idx: int
    dep_arr_day: str
    eq_code: str
    number: str
    deadhead: bool
    departure_station: str
    departure: Instant
    meal: str
    arrival_station: str
    arrival: Instant
    block: timedelta
    synth: timedelta
    ground: timedelta
    equipment_change: bool


class DutyPeriod(BaseModel):
    uuid: UUID
    compact_uuid: UUID
    idx: int
    report: Instant
    report_station: str
    release: Instant
    release_station: str
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    duty: timedelta
    flight_duty: timedelta
    layover: Layover | None
    flights: list[Flight]


class Trip(BaseModel):
    uuid: UUID
    compact_uuid: UUID
    number: str
    start: Instant
    end: Instant
    positions: list[str]
    operations: str
    qualifications: str
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    tafb: timedelta
    dutyperiods: list[DutyPeriod]


class Page(BaseModel):
    uuid: UUID
    base: str
    satellite_base: str
    equipment: str
    division: str
    issued: date
    effective: date
    start: date
    end: date
    trips: list[Trip]
    number: str


class BidPackage(BaseModel):
    uuid: UUID
    source: HashedFile | None
    pages: list[Page]

    # def default_file_name(self) -> str:
    #     return (
    #         f"{self.pages[0].start}_{self.pages[0].end}_{self.pages[0].base}"
    #         f"_expanded_{self.uuid}.json"
    #     )

    # @classmethod
    # def default_debug_file(cls, debug_dir: Path | None, name: str) -> Path | None:
    #     if debug_dir is None:
    #         return None
    #     return debug_dir / f"{name}_expanded-debug.txt"

    # def walk_trips(self) -> Iterable[Trip]:
    #     for page in self.pages:
    #         for trip in page.trips:
    #             yield trip

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, BidPackage):
            if self.source != __value.source:
                return False
            return (self.uuid, self.pages) == (__value.uuid, __value.pages)
        return super().__eq__(__value)


# @timers.timer_ns(time_logger)
# def load_expanded(file_in: Path) -> BidPackage:
#     bid_package = BidPackage.parse_file(file_in)
#     return bid_package


# @timers.timer_ns(time_logger)
# def save_expanded(
#     save_dir: Path, file_name: str | None, overwrite: bool, bid_package: BidPackage
# ):
#     if file_name is None:
#         file_out = save_dir / bid_package.default_file_name()
#     else:
#         file_out = save_dir / file_name
#     validate_file_out(file_out, overwrite=overwrite)
#     file_out.write_text(bid_package.json(indent=2))


class PackageBrowser:
    def __init__(self, package: BidPackage) -> None:
        self.package = package
        self._lookup: dict[str, Any] = {}

    def _init_lookup(self):
        for page in self.pages():
            self._lookup[str(page.uuid)] = page
        for trip in self.trips(None):
            self._lookup[str(trip.uuid)] = trip
        for dutyperiod in self.dutyperiods(None):
            self._lookup[str(dutyperiod.uuid)] = dutyperiod
        for flight in self.flights(None):
            self._lookup[str(flight.uuid)] = flight
        for layover in self.layovers():
            if layover is not None:
                self._lookup[str(layover.uuid)] = layover

    def lookup(self, uuid: UUID):
        # TODO catch missing uuids
        if not self._lookup:
            self._init_lookup()
        return self._lookup[str(uuid)]

    @classmethod
    def file_name_stub(cls, bid_package: BidPackage) -> str:
        return (
            f"{bid_package.pages[0].start}_{bid_package.pages[0].end}_"
            f"{bid_package.pages[0].base}_{bid_package.uuid}"
        )

    @classmethod
    def default_file_name(cls, bid_package: BidPackage) -> str:
        hash_stub = ""
        if bid_package.source is not None:
            hash_stub = f"-{bid_package.source.file_hash}"
        return f"{cls.file_name_stub(bid_package)}{hash_stub}-expanded.json"
        # return (
        #     f"{bid_package.pages[0].start}_{bid_package.pages[0].end}_"
        #     f"{bid_package.pages[0].base}_{bid_package.uuid}{hash_stub}-expanded.json"
        # )

    @classmethod
    def default_debug_file(
        cls, debug_dir: Path | None, bid_package: BidPackage
    ) -> Path | None:
        # FIXME refactor to act the same as default_file_name
        if debug_dir is None:
            return None
        return Path(f"{cls.file_name_stub(bid_package)}-expanded-debug.txt")
        # return Path(
        #     f"{bid_package.pages[0].start}_{bid_package.pages[0].end}_"
        #     f"{bid_package.pages[0].base}_{bid_package.uuid}_expanded-debug.txt"
        # )

    def pages(self) -> Generator[Page, None, None]:
        for page in self.package.pages:
            yield page

    def trips(self, page: Page | None) -> Generator[Trip, None, None]:
        if page is None:
            for page_a in self.pages():
                for trip_a in page_a.trips:
                    yield trip_a
        else:
            for trip in page.trips:
                yield trip

    def dutyperiods(self, trip: Trip | None) -> Generator[DutyPeriod, None, None]:
        if trip is None:
            for trip_a in self.trips(None):
                for dutyperiod in trip_a.dutyperiods:
                    yield dutyperiod
        else:
            for dutyperiod in trip.dutyperiods:
                yield dutyperiod

    def flights(self, dutyperiod: DutyPeriod | None) -> Generator[Flight, None, None]:
        if dutyperiod is None:
            for dutyperiod_a in self.dutyperiods(None):
                for flight in dutyperiod_a.flights:
                    yield flight
        else:
            for flight in dutyperiod.flights:
                yield flight

    def layovers(self) -> Generator[Layover, None, None]:
        for dutyperiod in self.dutyperiods(None):
            if dutyperiod.layover is None:
                continue
            yield dutyperiod.layover


class Stats:
    # TODO usd this class to generate stats
    pass


def save_json(
    file_out: Path,
    bid_package: BidPackage,
    overwrite: bool = False,
    indent: int = 2,
):
    serializer = SerializePydantic[BidPackage]()
    serializer.save_json(
        file_out=file_out, data=bid_package, overwrite=overwrite, indent=indent
    )


def load_json(
    file_in: Path,
    strict: bool | None = None,
    context: dict[str, Any] | None = None,
) -> BidPackage:
    serializer = SerializePydantic[BidPackage]()
    data = serializer.load_json(
        file_in=file_in, model=BidPackage, strict=strict, context=context
    )
    return data
