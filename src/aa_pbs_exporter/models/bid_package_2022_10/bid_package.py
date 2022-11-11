from datetime import datetime, timedelta
from uuid import UUID

from pydantic import BaseModel
from aa_pbs_exporter.airports.airport_model import Airport


class LineReference(BaseModel):
    source: str
    from_line: int
    to_line: int


class Transportation(BaseModel):
    name: str
    phone: str


class Hotel(BaseModel):
    name: str
    phone: str
    transportation: Transportation | None


class Layover(BaseModel):
    odl: timedelta
    city: str
    hotel: Hotel | None
    additional_hotel: Hotel | None


class Flight(BaseModel):
    dutyperiod_index: int
    idx: int
    dep_arr_day: str
    eq_code: str
    number: str
    deadhead: bool
    departure_station: str
    departure_time: datetime
    meal: str
    arrival_station: str
    arrival_time: datetime
    block: timedelta
    synth: timedelta
    ground: timedelta
    equipment_change: bool


class DutyPeriod(BaseModel):
    idx: int
    report: datetime
    report_station: str
    release: datetime
    release_station: str
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    duty: timedelta
    flight_duty: timedelta
    flights: list[Flight]
    layover: Layover | None


class Trip(BaseModel):
    uuid: UUID
    number: str
    base: str
    satelite_base: str
    positions: str
    operations: str
    division: str
    equipment: str
    special_qualifications: bool
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    tafb: timedelta
    dutyperiods: list[DutyPeriod]
    line_ref: LineReference | None


class BidPackage(BaseModel):
    source: str
    base: str
    satelite_bases: set[str]
    from_date: datetime
    to_date: datetime
    trips: list[Trip]
    airports: dict[str, Airport]
