"""
The compact model represents the pairing package in its most compact form. It contains
all the info needed to expand trips with fully defined dates and times.
"""

from datetime import date, time, timedelta

from pydantic import BaseModel


class Transportation(BaseModel):
    name: str
    phone: str


class Hotel(BaseModel):
    name: str
    phone: str | None


class LclHbt(BaseModel):
    lcl: time
    hbt: time
    tz_name: str


class Layover(BaseModel):
    odl: timedelta
    city: str
    hotel: Hotel | None
    transportation: Transportation | None
    hotel_additional: Hotel | None
    transportation_additional: Transportation | None


class Flight(BaseModel):
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
    # uuid: UUID
    number: str
    positions: list[str]
    operations: str
    special_qualifications: bool
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    tafb: timedelta
    dutyperiods: list[DutyPeriod]
    start_dates: list[date]


class Page(BaseModel):
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
    source: str
    pages: list[Page]

    def default_file_name(self)->str:
        return f"{self.pages[0].start}_{self.pages[0].end}_{self.pages[0].base}_compact"
