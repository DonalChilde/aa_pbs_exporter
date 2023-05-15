"""
The compact model represents the pairing package in its most compact form. It contains
all the info needed to expand trips with fully defined dates and times.
uuids match the source raw model uuids.
"""

from datetime import date, time, timedelta
from typing import Iterable
from uuid import UUID

from pydantic import BaseModel

from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile


class Transportation(BaseModel):
    uuid: UUID
    name: str
    phone: str


class Hotel(BaseModel):
    uuid: UUID
    name: str
    phone: str | None


class HotelInfo(BaseModel):
    hotel: Hotel | None
    transportation: Transportation | None


class LclHbt(BaseModel):
    lcl: time
    hbt: time
    tz_name: str


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

    # def sum_synth(self) -> timedelta:
    #     total = timedelta()
    #     for dutyperiod in self.dutyperiods:
    #         total += dutyperiod.synth
    #     return total

    # def sum_total_pay(self) -> timedelta:
    #     total = timedelta()
    #     for dutyperiod in self.dutyperiods:
    #         total += dutyperiod.total_pay
    #     return total


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


class BidPackage(BaseModel):
    uuid: UUID
    source: HashedFile | None
    pages: list[Page]

    def walk_trips(self) -> Iterable[Trip]:
        for page in self.pages:
            for trip in page.trips:
                yield trip

    def default_file_name(self) -> str:
        return f"{self.pages[0].start}_{self.pages[0].end}_{self.pages[0].base}_compact.json"
