"""
The compact model represents the pairing package in its most compact form. It contains
all the info needed to expand trips with fully defined dates and times.
uuids match the source raw model uuids.
"""

import logging
from datetime import date, time, timedelta
from pathlib import Path
from typing import Iterable
from uuid import UUID

from pydantic import BaseModel

from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.timers import timers
from aa_pbs_exporter.pbs_2022_01.helpers import instant_time as instant

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

    def sum_block(self) -> timedelta:
        total = timedelta()
        for flight in self.flights:
            total += flight.block
        return total

    def sum_synth(self) -> timedelta:
        total = timedelta()
        for flight in self.flights:
            total += flight.synth
        return total


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

    def sum_block(self) -> timedelta:
        total = timedelta()
        for dutyperiod in self.dutyperiods:
            total += dutyperiod.block
        return total


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

    def walk_trips(self) -> Iterable[Trip]:
        for page in self.pages:
            for trip in page.trips:
                yield trip

    def default_file_name(self) -> str:
        return (
            f"{self.pages[0].start}_{self.pages[0].end}_{self.pages[0].base}"
            f"_compact_{self.uuid}.json"
        )

    @classmethod
    def default_debug_file(cls, debug_dir: Path | None, name: str) -> Path | None:
        if debug_dir is None:
            return None
        return debug_dir / f"{name}_compact-debug.txt"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, BidPackage):
            if self.source != __value.source:
                return False
            return (self.uuid, self.pages) == (__value.uuid, __value.pages)
        return super().__eq__(__value)


@timers.timer_ns(time_logger)
def load_compact(file_in: Path) -> BidPackage:
    bid_package = BidPackage.parse_file(file_in)
    return bid_package


@timers.timer_ns(time_logger)
def save_compact(
    save_dir: Path, file_name: str | None, overwrite: bool, bid_package: BidPackage
):
    if file_name is None:
        file_out = save_dir / bid_package.default_file_name()
    else:
        file_out = save_dir / file_name
    validate_file_out(file_out, overwrite=overwrite)
    file_out.write_text(bid_package.json(indent=2))
