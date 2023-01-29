"""
    _summary_

Assumptions:
    - Structures are complete after parsing.
    - Each dutyperiod has a layover with an odl unless its the last dutyperiod
    - The release tz and station is the same as the report tz and station.
      - not sure how often this would come up. and it may not be a problem. 
    - The start date of a bid is the same as the effective date in the page footer.
"""
from dataclasses import dataclass, field

from aa_pbs_exporter.snippets.parsing.parsed_indexed_string import ParsedIndexedString

TAB = "\t"
NL = "\n"


@dataclass
class PageHeader1(ParsedIndexedString):
    # source: IndexedString
    pass


@dataclass
class PageHeader2(ParsedIndexedString):
    # source: IndexedString
    calendar_range: str


@dataclass
class HeaderSeparator(ParsedIndexedString):
    # source: IndexedString
    pass


@dataclass
class BaseEquipment(ParsedIndexedString):
    # source: IndexedString
    base: str
    satelite_base: str
    equipment: str


@dataclass
class TripHeader(ParsedIndexedString):
    # source: IndexedString
    number: str
    ops_count: str
    positions: str
    operations: str
    special_qualification: str
    calendar: str


@dataclass
class DutyPeriodReport(ParsedIndexedString):
    # source: IndexedString
    report: str
    calendar: str


@dataclass
class Flight(ParsedIndexedString):
    # source: IndexedString
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


@dataclass
class DutyPeriodRelease(ParsedIndexedString):
    # source: IndexedString
    release: str
    block: str
    synth: str
    total_pay: str
    duty: str
    flight_duty: str
    calendar: str


@dataclass
class Hotel(ParsedIndexedString):
    # source: IndexedString
    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: str


@dataclass
class HotelAdditional(ParsedIndexedString):
    # source: IndexedString
    layover_city: str
    name: str
    phone: str
    calendar: str


@dataclass
class Transportation(ParsedIndexedString):
    # source: IndexedString
    name: str
    phone: str
    calendar: str


@dataclass
class TransportationAdditional(ParsedIndexedString):
    # source: IndexedString
    name: str
    phone: str
    calendar: str


@dataclass
class TripFooter(ParsedIndexedString):
    # source: IndexedString
    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: str


@dataclass
class TripSeparator(ParsedIndexedString):
    # source: IndexedString
    pass


@dataclass
class PageFooter(ParsedIndexedString):
    # source: IndexedString
    issued: str
    effective: str
    base: str
    satelite_base: str
    equipment: str
    division: str
    page: str


@dataclass
class PackageDate(ParsedIndexedString):
    # source: IndexedString
    month: str
    year: str


@dataclass
class Layover:
    hotel: Hotel
    transportation: Transportation | None = None
    hotel_additional: HotelAdditional | None = None
    transportation_additional: TransportationAdditional | None = None

    def __str__(self) -> str:
        return self._indent_str()

    def _indent_str(self, indent: str = "  ", indent_level: int = 0):
        if self.transportation:
            transportation = self.transportation._indent_str(indent, indent_level + 1)
        else:
            transportation = f"{indent*(indent_level+1)}No transportation"
        if self.hotel_additional:
            add_hotel = self.hotel_additional._indent_str(indent, indent_level + 1)
        else:
            add_hotel = f"{indent*(indent_level+1)}No additional hotel"
        if self.transportation_additional:
            add_trans = self.transportation_additional._indent_str(
                indent, indent_level + 1
            )
        else:
            add_trans = f"{indent*(indent_level+1)}No additional transportation"
        return (
            f"{indent*indent_level}Layover:"
            f"\n{self.hotel._indent_str(indent,indent_level+1)}"
            f"\n{transportation}"
            f"\n{add_hotel}"
            f"\n{add_trans}"
        )


@dataclass
class DutyPeriod:
    report: DutyPeriodReport
    release: DutyPeriodRelease | None = None
    layover: Layover | None = None
    flights: list[Flight] = field(default_factory=list)

    def __str__(self) -> str:
        return self._indent_str()

    def _indent_str(self, indent: str = "  ", indent_level: int = 0) -> str:
        if self.release is not None:
            release = self.release._indent_str(indent, indent_level + 2)
        else:
            release = f"{indent*(indent_level+2)}No release"
        if self.layover is not None:
            layover = f"{self.layover._indent_str(indent,indent_level+1)}"
        else:
            layover = f"{indent*(indent_level+2)}No layover"
        flight_strings = []
        for flight in self.flights:
            flight_strings.append(f"{flight._indent_str(indent,indent_level+2)}")
        return (
            f"{indent*indent_level}DutyPeriod:"
            f"\n{indent*(indent_level+1)}Report:"
            f"\n{self.report._indent_str(indent,indent_level+2)}"
            f"\n{indent*(indent_level+1)}Flights:"
            f"\n{NL.join(flight_strings)}"
            f"\n{indent*(indent_level+1)}Release:"
            f"\n{release}"
            # f"\n{indent*(indent_level+1)}Layover:"
            f"\n{layover}"
        )


@dataclass
class Trip:
    header: TripHeader
    footer: TripFooter | None = None
    dutyperiods: list[DutyPeriod] = field(default_factory=list)

    def __str__(self) -> str:
        return self._indent_str()

    def _indent_str(self, indent: str = "  ", indent_level: int = 0):
        if self.footer:
            footer = self.footer._indent_str(indent, indent_level + 2)
        else:
            footer = f"{indent*(indent_level+2)}No footer"
        dp_strings = []
        for dutyperiod in self.dutyperiods:
            dp_strings.append(dutyperiod._indent_str(indent, indent_level + 2))
        return (
            f"{indent*indent_level}Trip:"
            f"\n{indent*(indent_level+1)}Header:"
            f"\n{self.header._indent_str(indent,indent_level+2)}"
            f"\n{indent*(indent_level+1)}DutyPeriods:"
            f"\n{NL.join(dp_strings)}"
            f"\n{indent*(indent_level+1)}Footer:"
            f"\n{footer}"
        )


@dataclass
class Page:
    page_header_1: PageHeader1
    page_header_2: PageHeader2 | None = None
    base_equipment: BaseEquipment | None = None
    page_footer: PageFooter | None = None
    trips: list[Trip] = field(default_factory=list)


@dataclass
class BidPackage:
    source: str
    # package_date: PackageDate | None
    pages: list[Page] = field(default_factory=list)
