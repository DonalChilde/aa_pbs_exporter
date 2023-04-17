"""
    _summary_

Assumptions:
    - Structures are complete after parsing.
    - Each dutyperiod has a layover with an odl unless its the last dutyperiod
    - The release tz and station is the same as the next report tz and station.
      - not sure how often this would come up. and it may not be a problem.
    - The start date of a bid is the same as the effective date in the page footer.
"""

import json

from pydantic import BaseModel

# TAB = "\t"
NL = "\n"


class IndexedString(BaseModel):
    idx: int
    txt: str

    def __str__(self) -> str:
        return f"{self.idx}: {self.txt!r}"


class ParsedIndexedString(BaseModel):
    source: IndexedString

    def __str__(self) -> str:
        data = self.dict()
        data.pop("source", None)
        return f"{self.source}\n\t{self.__class__.__name__}: {json.dumps(data)}"


class PageHeader1(ParsedIndexedString):

    pass


class PageHeader2(ParsedIndexedString):

    from_date: str
    to_date: str


class HeaderSeparator(ParsedIndexedString):

    pass


class BaseEquipment(ParsedIndexedString):

    base: str
    satellite_base: str
    equipment: str


class TripHeader(ParsedIndexedString):

    number: str
    ops_count: str
    positions: str
    operations: str
    special_qualification: str
    calendar: str


class DutyPeriodReport(ParsedIndexedString):

    report: str
    calendar: str


class Flight(ParsedIndexedString):

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


class DutyPeriodRelease(ParsedIndexedString):

    release: str
    block: str
    synth: str
    total_pay: str
    duty: str
    flight_duty: str
    calendar: str


class Hotel(ParsedIndexedString):

    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: str


class HotelAdditional(ParsedIndexedString):

    layover_city: str
    name: str
    phone: str
    calendar: str


class Transportation(ParsedIndexedString):

    name: str
    phone: str
    calendar: str


class TransportationAdditional(ParsedIndexedString):

    name: str
    phone: str
    calendar: str


class TripFooter(ParsedIndexedString):

    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: str


class TripSeparator(ParsedIndexedString):

    pass


class PageFooter(ParsedIndexedString):

    issued: str
    effective: str
    base: str
    satelite_base: str
    equipment: str
    division: str
    page: str


class PackageDate(ParsedIndexedString):

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
