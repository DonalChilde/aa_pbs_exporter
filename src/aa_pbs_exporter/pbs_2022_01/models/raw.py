"""
    _summary_

Assumptions:
    - Structures are complete after parsing.
    - Each dutyperiod has a layover with an odl unless its the last dutyperiod
    - The release tz and station is the same as the next report tz and station.
      - not sure how often this would come up. and it may not be a problem.
    - The start date of a bid is the same as the effective date in the page footer.
    - uuids are built from the indexed string the data is parsed from. uuids should
      be reproducible so long as the source document does not change - including line
      numbers.
"""

import json
from typing import Iterable
from uuid import UUID, uuid5

from pydantic import BaseModel

from aa_pbs_exporter.pbs_2022_01 import PARSER_DNS
from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile

LAYOVER_DNS = uuid5(PARSER_DNS, "LAYOVER_DNS")
DUTYPERIOD_DNS = uuid5(PARSER_DNS, "DUTYPERIOD_DNS")
TRIP_DNS = uuid5(PARSER_DNS, "TRIP_DNS")
PAGE_DNS = uuid5(PARSER_DNS, "PAGE_DNS")
BIDPACKAGE_DNS = uuid5(PARSER_DNS, "BIDPACKAGE_DNS")
# TAB = "\t"
NL = "\n"


class IndexedString(BaseModel):
    idx: int
    txt: str

    # TODO move to common, try classmethod factory?
    def __str__(self) -> str:
        return f"{self.idx}: {self.txt!r}"

    def str_with_uuid(self, uuid: UUID) -> str:
        return f"{self.idx}:{self.uuid5(uuid)}:{self.txt!r}"

    def uuid5(self, uuid: UUID) -> UUID:
        return uuid5(uuid, f"{self.idx}: {self.txt!r}")


def indexed_string_factory(idx: int, txt: str) -> IndexedString:
    return IndexedString(idx=idx, txt=txt)


class ParsedIndexedString(BaseModel):
    source: IndexedString

    def __str__(self) -> str:
        data = self.dict()
        data.pop("source", None)
        return f"{self.source}\n\t{self.__class__.__name__}: {json.dumps(data)}"

    def str_with_uuid(self) -> str:
        data = self.dict()
        data.pop("source", None)
        return f"{self.source.str_with_uuid(PARSER_DNS)}\n\t{self.__class__.__name__}: {json.dumps(data)}"

    def uuid5(self) -> UUID:
        return self.source.uuid5(PARSER_DNS)


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
    # calendar: str


class DutyPeriodReport(ParsedIndexedString):
    report: str
    calendar: list[str] = []


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
    calendar: list[str] = []


class DutyPeriodRelease(ParsedIndexedString):
    release: str
    block: str
    synth: str
    total_pay: str
    duty: str
    flight_duty: str
    calendar: list[str] = []


class Hotel(ParsedIndexedString):
    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: list[str] = []


class HotelAdditional(ParsedIndexedString):
    layover_city: str
    name: str
    phone: str
    calendar: list[str] = []


class Transportation(ParsedIndexedString):
    name: str
    phone: str
    calendar: list[str] = []


class TransportationAdditional(ParsedIndexedString):
    name: str
    phone: str
    calendar: list[str] = []


class TripFooter(ParsedIndexedString):
    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: list[str] = []


class CalendarOnly(ParsedIndexedString):
    calendar: list[str] = []


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


# class PackageDate(ParsedIndexedString):
#     month: str
#     year: str


class Layover(BaseModel):
    uuid: UUID
    hotel: Hotel
    transportation: Transportation | None = None
    hotel_additional: HotelAdditional | None = None
    transportation_additional: TransportationAdditional | None = None

    def uuid5(self) -> UUID:
        return self.hotel.source.uuid5(LAYOVER_DNS)


class DutyPeriod(BaseModel):
    uuid: UUID
    report: DutyPeriodReport
    flights: list[Flight]
    release: DutyPeriodRelease | None = None
    layover: Layover | None = None

    def uuid5(self) -> UUID:
        return self.report.source.uuid5(DUTYPERIOD_DNS)


class Trip(BaseModel):
    uuid: UUID
    header: TripHeader
    dutyperiods: list[DutyPeriod]
    footer: TripFooter | None = None
    calendar_only: CalendarOnly | None = None
    calendar_entries: list[str] = []

    def uuid5(self) -> UUID:
        return self.header.source.uuid5(TRIP_DNS)


class Page(BaseModel):
    uuid: UUID
    page_header_1: PageHeader1
    page_header_2: PageHeader2 | None = None
    base_equipment: BaseEquipment | None = None
    page_footer: PageFooter | None = None
    trips: list[Trip]

    def uuid5(self) -> UUID:
        return self.page_header_1.source.uuid5(PAGE_DNS)


class BidPackage(BaseModel):
    uuid: UUID
    source: HashedFile | None
    pages: list[Page]

    def default_file_name(self) -> str:
        assert self.pages[0].page_footer is not None
        return f"{self.pages[0].page_footer.effective}_{self.pages[0].page_footer.base}_raw"

    def uuid5(self) -> UUID:
        if self.source:
            uuid_seed = self.source.file_hash
        else:
            uuid_seed = "None"
        return uuid5(BIDPACKAGE_DNS, uuid_seed)

    def walk_trips(self) -> Iterable[Trip]:
        for page in self.pages:
            for trip in page.trips:
                yield trip
