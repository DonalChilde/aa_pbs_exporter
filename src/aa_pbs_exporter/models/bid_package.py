# pylint: disable=missing-docstring

from dataclasses import dataclass, field
from datetime import date, time, timedelta
from typing import List, Optional, Set


@dataclass
class BidPackage:
    date_from: date
    date_to: date
    base: Set[str] = field(default_factory=set)
    equipment: Set[str] = field(default_factory=set)
    satelite_bases: Set[str] = field(default_factory=set)
    bid_sequences: List["BidSequence"] = field(default_factory=list)
    source: str = ""


@dataclass
class ThreePartStatus:
    base: str
    equipment: str
    division: str


@dataclass
class BidSequence:
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
    positions: Set[str] = field(default_factory=set)
    operations: Set[str] = field(default_factory=set)
    special_qualification: bool = False
    start_dates: List[date] = field(default_factory=list)
    duty_periods: List["DutyPeriod"] = field(default_factory=list)
    prior_month_sequence: Optional[str] = None
    prior_month_date: Optional[str] = None


@dataclass
class DutyPeriod:
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
    flights: List["Flight"] = field(default_factory=list)
    hotels: List["Hotel"] = field(default_factory=list)


@dataclass
class Flight:
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


@dataclass
class Hotel:
    name: str
    phone: str | None
    transportation: Optional["Transportation"] = None


@dataclass
class Transportation:
    name: str
    phone: str | None = None
