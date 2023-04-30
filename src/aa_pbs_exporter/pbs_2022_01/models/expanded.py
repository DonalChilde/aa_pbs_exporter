from datetime import date, timedelta
from uuid import UUID, uuid5

from pydantic import BaseModel

from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile, Instant


class Transportation(BaseModel):
    uuid: UUID
    # compact_uuid:UUID
    name: str
    phone: str


class Hotel(BaseModel):
    uuid: UUID
    # compact_uuid:UUID
    name: str
    phone: str | None


class Layover(BaseModel):
    uuid: UUID
    # compact_uuid:UUID
    odl: timedelta
    city: str
    hotel: Hotel | None
    transportation: Transportation | None
    hotel_additional: Hotel | None
    transportation_additional: Transportation | None


class Flight(BaseModel):
    uuid: UUID
    compact_uuid: UUID
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
    special_qualifications: bool
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


class BidPackage(BaseModel):
    uuid: UUID
    source: HashedFile | None
    pages: list[Page]

    def default_file_name(self) -> str:
        return (
            f"{self.pages[0].start}_{self.pages[0].end}_{self.pages[0].base}_expanded"
        )
