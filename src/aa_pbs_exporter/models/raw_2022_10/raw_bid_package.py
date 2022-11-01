from dataclasses import dataclass, field
from typing import List


@dataclass
class SourceText:
    line_no: int
    txt: str

    def __repr__(self):
        return f"{self.line_no}: {self.txt}"


@dataclass
class PageHeader1:
    source: SourceText


@dataclass
class PageHeader2:
    source: SourceText
    calendar_range: str


@dataclass
class HeaderSeparator:
    source: SourceText


@dataclass
class BaseEquipment:
    source: SourceText
    base: str
    satelite_base: str
    equipment: str


@dataclass
class TripHeader:
    source: SourceText
    number: str
    ops_count: str
    positions: str
    operations: str
    special_qualification: str
    calendar: str


@dataclass
class DutyPeriodReport:
    source: SourceText
    report: str
    calendar: str


@dataclass
class Flight:
    source: SourceText
    dutyperiod_index: str
    d_a: str
    eq_code: str
    flight_number: str
    deadhead: str
    departure_station: str
    departure_time: str
    meal: str
    arrival_station: str
    arrival_time: str
    block: str
    synth: str
    ground: str
    equipment_change: str
    calendar: str


@dataclass
class DuytPeriodRelease:
    source: SourceText
    release: str
    block: str
    synth: str
    total_pay: str
    duty: str
    flight_duty: str
    calendar: str


@dataclass
class Hotel:
    source: SourceText
    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: str


@dataclass
class HotelAdditional:
    source: SourceText
    layover_city: str
    name: str
    phone: str
    calendar: str


@dataclass
class Transportation:
    source: SourceText
    name: str
    phone: str
    calendar: str


@dataclass
class TransportationAdditional:
    source: SourceText
    name: str
    phone: str
    calendar: str


@dataclass
class TripFooter:
    source: SourceText
    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: str


@dataclass
class TripSeparator:
    source: SourceText


@dataclass
class PageFooter:
    source: SourceText
    issued: str
    effective: str
    base: str
    satelite_base: str
    equipment: str
    division: str
    page: str


@dataclass
class PackageDate:
    source: SourceText
    month: str
    year: str


@dataclass
class DutyPeriod:
    report: DutyPeriodReport
    release: DuytPeriodRelease | None = None
    hotel: Hotel | None = None
    transportation: Transportation | None = None
    hotel_additional: HotelAdditional | None = None
    transportation_additional: TransportationAdditional | None = None
    flights: List[Flight] = field(default_factory=list)


@dataclass
class Trip:
    header: TripHeader
    footer: TripFooter | None = None
    calendar: List = field(default_factory=list)
    dutyperiods: List[DutyPeriod] = field(default_factory=list)


@dataclass
class Page:
    page_header_1: PageHeader1
    page_header_2: PageHeader2 | None = None
    base_equipment: BaseEquipment | None = None
    page_footer: PageFooter | None = None
    trips: List[Trip] = field(default_factory=list)


@dataclass
class Package:
    file_name: str
    # package_date: PackageDate | None
    pages: List[Page] = field(default_factory=list)
