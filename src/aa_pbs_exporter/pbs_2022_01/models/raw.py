"""
    _summary_

Assumptions:
    - Structures are complete after parsing.
    - Each dutyperiod has a layover with an odl unless its the last dutyperiod
    - The release tz and station is the same as the report tz and station.
      - not sure how often this would come up. and it may not be a problem. 
    - The start date of a bid is the same as the effective date in the page footer.
"""
# from dataclasses import dataclass, field
from pydantic import BaseModel

from aa_pbs_exporter.snippets.parsing.parsed_indexed_string import ParsedIndexedString

TAB = "\t"
NL = "\n"


class IndexedString(BaseModel):
    idx: int
    txt: str


class PageHeader1(BaseModel):
    source: IndexedString


class PageHeader2(BaseModel):
    source: IndexedString
    calendar_range: str


class HeaderSeparator(BaseModel):
    source: IndexedString


class BaseEquipment(BaseModel):
    source: IndexedString
    base: str
    satelite_base: str
    equipment: str


class TripHeader(BaseModel):
    source: IndexedString
    number: str
    ops_count: str
    positions: str
    operations: str
    special_qualification: str
    calendar: str


class DutyPeriodReport(BaseModel):
    source: IndexedString
    report: str
    calendar: str


class Flight(BaseModel):
    source: IndexedString
    dutyperiod_idx: str
    dep_arr_day: str
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


class DutyPeriodRelease(BaseModel):
    source: IndexedString
    release: str
    block: str
    synth: str
    total_pay: str
    duty: str
    flight_duty: str
    calendar: str


class Hotel(BaseModel):
    source: IndexedString
    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: str


class HotelAdditional(BaseModel):
    source: IndexedString
    layover_city: str
    name: str
    phone: str
    calendar: str


class Transportation(BaseModel):
    source: IndexedString
    name: str
    phone: str
    calendar: str


class TransportationAdditional(BaseModel):
    source: IndexedString
    name: str
    phone: str
    calendar: str


class TripFooter(BaseModel):
    source: IndexedString
    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: str


class TripSeparator(BaseModel):
    source: IndexedString


class PageFooter(BaseModel):
    source: IndexedString
    issued: str
    effective: str
    base: str
    satelite_base: str
    equipment: str
    division: str
    page: str


class PackageDate(BaseModel):
    source: IndexedString
    month: str
    year: str


class Layover(BaseModel):
    hotel: Hotel
    transportation: Transportation | None = None
    hotel_additional: HotelAdditional | None = None
    transportation_additional: TransportationAdditional | None = None


class DutyPeriod(BaseModel):
    report: DutyPeriodReport
    flights: list[Flight]
    release: DutyPeriodRelease | None = None
    layover: Layover | None = None


class Trip(BaseModel):
    header: TripHeader
    dutyperiods: list[DutyPeriod]
    footer: TripFooter | None = None


class Page(BaseModel):
    page_header_1: PageHeader1
    page_header_2: PageHeader2 | None = None
    base_equipment: BaseEquipment | None = None
    page_footer: PageFooter | None = None
    trips: list[Trip]


class BidPackage(BaseModel):
    source: str
    pages: list[Page]
