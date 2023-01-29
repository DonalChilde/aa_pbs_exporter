from dataclasses import dataclass, field
from datetime import datetime, timedelta


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

# class LocalHbt(TypedDict):
#     local: str
#     hbt: str


@dataclass
class SourceReference:
    source: str
    from_line: int
    to_line: int


@dataclass
class Transportation:
    name: str
    phone: str


@dataclass
class Hotel:
    name: str
    phone: str | None


@dataclass
class Layover:
    odl: timedelta
    city: str
    hotel: Hotel | None
    transportation: Transportation | None
    hotel_additional: Hotel | None
    transportation_additional: Transportation | None


@dataclass
class Flight:
    dutyperiod_idx: int
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


@dataclass
class DutyPeriod:
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
    layover: Layover | None
    flights: list[Flight] = field(default_factory=list)


@dataclass
class Trip:
    # uuid: UUID
    number: str
    # base: str
    # satelite_base: str
    positions: str
    operations: str
    # division: str
    # equipment: str
    special_qualifications: bool
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    tafb: timedelta
    # source_ref: SourceReference | None
    dutyperiods: list[DutyPeriod] = field(default_factory=list)


@dataclass
class Page:
    base: str
    satellite_base: str
    equipment: str
    division: str
    issued: datetime
    effective: datetime
    start: datetime
    end: datetime
    trips: list[Trip] = field(default_factory=list)


@dataclass
class BidPackage:
    source: str
    pages: list[Page] = field(default_factory=list)
