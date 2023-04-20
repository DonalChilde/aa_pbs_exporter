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
    tz_name: str

    def local(self, tz_name: str | None = None) -> datetime:
        if tz_name is None:
            return self.utc_date.astimezone(tz=ZoneInfo(self.tz_name))
        return self.utc_date.astimezone(tz=ZoneInfo(tz_name))

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

    def default_file_name(self) -> str:
        return (
            f"{self.pages[0].start}_{self.pages[0].end}_{self.pages[0].base}_expanded"
        )
