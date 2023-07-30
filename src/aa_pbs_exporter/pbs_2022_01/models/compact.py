"""
The compact model represents the pairing package in its most compact form. It contains
all the info needed to expand trips with fully defined dates and times.
uuids match the source raw model uuids.
"""

import logging
from collections.abc import Generator
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from aa_pbs_exporter.pbs_2022_01.helpers import instant_time as instant
from aa_pbs_exporter.pbs_2022_01.helpers.serialize_pydantic import SerializePydantic
from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
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


class LclHbt(BaseModel):
    lcl: instant.InstantTime
    hbt: instant.InstantTime


class Layover(BaseModel):
    uuid: UUID
    odl: timedelta
    city: str
    hotel_info: list[HotelInfo]


class Flight(BaseModel):
    uuid: UUID
    dp_idx: int
    idx: int
    dep_arr_day: str
    eq_code: str
    number: str
    deadhead: bool
    departure_station: str
    departure: LclHbt
    meal: str
    arrival_station: str
    arrival: LclHbt
    block: timedelta
    synth: timedelta
    ground: timedelta
    equipment_change: bool


class DutyPeriod(BaseModel):
    uuid: UUID
    idx: int
    report: LclHbt
    report_station: str
    release: LclHbt
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
    number: str
    positions: list[str]
    operations: str
    qualifications: str
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    tafb: timedelta
    dutyperiods: list[DutyPeriod]
    start_dates: list[date]


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

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, BidPackage):
            if self.source != __value.source:
                return False
            return (self.uuid, self.pages) == (__value.uuid, __value.pages)
        return super().__eq__(__value)


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
    def default_file_name(cls, bid_package: BidPackage) -> str:
        return (
            f"{bid_package.pages[0].start}_{bid_package.pages[0].end}_"
            f"{bid_package.pages[0].base}_{bid_package.uuid}_compact.json"
        )

    @classmethod
    def default_debug_file(
        cls, debug_dir: Path | None, bid_package: BidPackage
    ) -> Path | None:
        if debug_dir is None:
            return None
        return Path(
            f"{bid_package.pages[0].start}_{bid_package.pages[0].end}_"
            f"{bid_package.pages[0].base}_{bid_package.uuid}_compact-debug.txt"
        )

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
