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
import logging
from pathlib import Path
from typing import Iterable
from uuid import NAMESPACE_DNS, UUID, uuid5

from pydantic import BaseModel

from aa_pbs_exporter.pbs_2022_01 import PARSER_DNS
from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.timers.function_timer import function_timer

logger = logging.getLogger(__name__)
BIDPACKAGE_DNS = uuid5(PARSER_DNS, "BIDPACKAGE_DNS")
NL = "\n"


class IndexedString(BaseModel):
    idx: int
    txt: str

    # TODO move to common, try classmethod factory?
    def __str__(self) -> str:
        return f"{self.idx}: {self.txt!r}"

    def str_with_uuid(self, ns_uuid: UUID = NAMESPACE_DNS) -> str:
        return f"{self.idx}:{self.uuid5()}:{self.txt!r}"

    def uuid5(self, ns_uuid: UUID = NAMESPACE_DNS) -> UUID:
        return uuid5(ns_uuid, f"{self.idx}: {self.txt!r}")


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
        return f"{self.source.str_with_uuid()}\n\t{self.__class__.__name__}: {json.dumps(data)}"

    def uuid5(self) -> UUID:
        return self.source.uuid5()


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
    qualifications: str


class PriorMonthDeadhead(ParsedIndexedString):
    pass


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


class HotelInfo(BaseModel):
    hotel: Hotel | HotelAdditional | None
    transportation: Transportation | TransportationAdditional | None


class Layover(BaseModel):
    uuid: UUID
    layover_city: str
    rest: str
    hotel_info: list[HotelInfo]

    # def uuid5(self) -> UUID:
    #     return self.hotel_info[0].hotel.source.uuid5()


class DutyPeriod(BaseModel):
    uuid: UUID
    report: DutyPeriodReport
    flights: list[Flight]
    release: DutyPeriodRelease | None = None
    layover: Layover | None = None

    # def uuid5(self) -> UUID:
    #     return self.report.source.uuid5()


class Trip(BaseModel):
    uuid: UUID
    header: TripHeader
    dutyperiods: list[DutyPeriod]
    footer: TripFooter | None = None
    calendar_only: CalendarOnly | None = None
    calendar_entries: list[str] = []

    # def uuid5(self) -> UUID:
    #     return self.header.uuid5()


class Page(BaseModel):
    uuid: UUID
    page_header_1: PageHeader1
    page_header_2: PageHeader2 | None = None
    base_equipment: BaseEquipment | None = None
    page_footer: PageFooter | None = None
    trips: list[Trip]

    def uuid5(self) -> UUID:
        return self.page_header_1.source.uuid5()


class BidPackage(BaseModel):
    uuid: UUID
    source: HashedFile | None
    pages: list[Page]

    def default_file_name(self) -> str:
        assert self.pages[0].page_footer is not None
        return (
            f"{self.pages[0].page_footer.effective}_{self.pages[0].page_footer.base}"
            f"_raw_{self.uuid}.json"
        )

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

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, BidPackage):
            if self.source != __value.source:
                return False
            return (self.uuid, self.pages) == (__value.uuid, __value.pages)
        return super().__eq__(__value)


@function_timer(logger=logger, level=logging.INFO)
def load_raw(file_in: Path) -> BidPackage:
    bid_package = BidPackage.parse_file(file_in)
    return bid_package


@function_timer(logger=logger, level=logging.INFO)
def save_raw(
    save_dir: Path, file_name: str | None, overwrite: bool, bid_package: BidPackage
):
    if file_name is None:
        file_out = save_dir / bid_package.default_file_name()
    else:
        file_out = save_dir / file_name
    validate_file_out(file_out, overwrite=overwrite)
    file_out.write_text(bid_package.json(indent=2))
