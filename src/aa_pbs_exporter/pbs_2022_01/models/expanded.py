from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from pydantic import BaseModel

# TODO make validator class to allow passing out validation messages
# TODO split to expanded model, and expand functions? rename?
# TODO decide on parser version scheme, and rename packages
#   - pbs_2022_10
#       - parse
#       - models
#           - raw
#           - expanded
#       - validate
#       - convert


class Instant(BaseModel):
    utc_date: datetime
    local_tz: str

    def local(self) -> datetime:
        return self.utc_date.astimezone(tz=ZoneInfo(self.local_tz))


class SourceReference(BaseModel):
    source: str
    from_line: int
    to_line: int


class Transportation(BaseModel):
    name: str
    phone: str


class Hotel(BaseModel):
    name: str
    phone: str | None


class Layover(BaseModel):
    odl: timedelta
    city: str
    hotel: Hotel | None
    transportation: Transportation | None
    hotel_additional: Hotel | None
    transportation_additional: Transportation | None


class Flight(BaseModel):
    dutyperiod_idx: int
    idx: int
    dep_arr_day: str
    eq_code: str
    number: str
    deadhead: bool
    departure_station: str
    departure_time: Instant
    meal: str
    arrival_station: str
    arrival_time: Instant
    block: timedelta
    synth: timedelta
    ground: timedelta
    equipment_change: bool


class DutyPeriod(BaseModel):
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
    # uuid: UUID
    number: str
    start:datetime
    end:datetime
    positions: str
    operations: str
    special_qualifications: bool
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    tafb: timedelta
    dutyperiods: list[DutyPeriod]


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
