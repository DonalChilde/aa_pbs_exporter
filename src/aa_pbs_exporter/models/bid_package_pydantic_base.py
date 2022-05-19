# pylint: disable=missing-docstring
from datetime import date, time, timedelta
from typing import List, Optional, Set

from pydantic import BaseModel
from pydantic.json import timedelta_isoformat


class Transportation(BaseModel):
    name: str
    phone: str | None = None


class Hotel(BaseModel):
    name: str
    phone: str | None
    transportation: Optional[Transportation] = None


class Flight(BaseModel):
    day: str
    equipment_code: str
    flight_number: str
    deadhead: bool
    departure_station: str
    departure_local: time
    departure_home: time
    crewmeal: str
    arrival_station: str
    arrival_local: time
    arrival_home: time
    block: timedelta
    synth: timedelta
    ground: timedelta
    equipment_change: bool


class DutyPeriod(BaseModel):
    report_local: time
    report_home: time
    release_local: time
    release_home: time
    block: timedelta
    synth: timedelta
    total_pay: timedelta
    duty: timedelta
    flight_duty: timedelta
    rest: timedelta
    flights: List[Flight] = []  # = field(default_factory=list)
    hotels: List[Hotel] = []  # = field(default_factory=list)


class ThreePartStatus(BaseModel):
    base: str
    equipment: str
    division: str


class BidSequence(BaseModel):
    three_part: ThreePartStatus | None
    sequence_number: str
    ops_count: int
    total_block: timedelta
    synth: timedelta
    total_pay: timedelta
    tafb: timedelta
    internal_page: int
    from_line: int
    to_line: int
    positions: Set[str] = set()  # = field(default_factory=set)
    operations: Set[str] = set()  # = field(default_factory=set)
    start_dates: List[date] = []  # = field(default_factory=list)
    duty_periods: List[DutyPeriod] = []  # = field(default_factory=list)
    special_qualification: bool = False
    prior_month_sequence: Optional[str] = None
    prior_month_date: Optional[str] = None


class BidPackage(BaseModel):
    date_from: date
    date_to: date
    base: Set[str] = set()  # = field(default_factory=set)
    equipment: Set[str] = set()  # = field(default_factory=set)
    satelite_bases: Set[str] = set()  # = field(default_factory=set)
    bid_sequences: List[BidSequence] = []  # = field(default_factory=list)
    source: str = ""

    class Config:
        json_encoders = {timedelta: timedelta_isoformat}
