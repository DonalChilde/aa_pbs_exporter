from typing import TypedDict


class PageHeader1(TypedDict):
    pass


class PageHeader2(TypedDict):
    from_date: str
    to_date: str


class HeaderSeparator(TypedDict):
    pass


class BaseEquipment(TypedDict):
    base: str
    satellite_base: str
    equipment: str


class TripHeader(TypedDict):
    number: str
    ops_count: str
    positions: str
    operations: str
    qualifications: str


class PriorMonthDeadhead(TypedDict):
    pass


class DutyPeriodReport(TypedDict):
    report: str
    calendar: list[str]


class Flight(TypedDict):
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
    calendar: list[str]


class DutyPeriodRelease(TypedDict):
    release: str
    block: str
    synth: str
    total_pay: str
    duty: str
    flight_duty: str
    calendar: list[str]


class Layover(TypedDict):
    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: list[str]


class HotelAdditional(TypedDict):
    layover_city: str
    name: str
    phone: str
    calendar: list[str]


class Transportation(TypedDict):
    name: str
    phone: str
    calendar: list[str]


class TransportationAdditional(TypedDict):
    name: str
    phone: str
    calendar: list[str]


class TripFooter(TypedDict):
    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: list[str]


class CalendarOnly(TypedDict):
    calendar: list[str]


class TripSeparator(TypedDict):
    pass


class PageFooter(TypedDict):
    issued: str
    effective: str
    base: str
    satelite_base: str
    equipment: str
    division: str
    page: str


# TODO combine with raw_collected

# # class PackageDate(ParsedIndexedString):
# #     month: str
# #     year: str


# class HotelInfo(BaseModel):
#     hotel: Hotel | HotelAdditional | None
#     transportation: Transportation | TransportationAdditional | None


# class Layover(BaseModel):
#     uuid: UUID
#     layover_city: str
#     rest: str
#     hotel_info: list[HotelInfo]

#     # def uuid5(self) -> UUID:
#     #     return self.hotel_info[0].hotel.source.uuid5()


# class DutyPeriod(BaseModel):
#     uuid: UUID
#     report: DutyPeriodReport
#     flights: list[Flight]
#     release: DutyPeriodRelease | None = None
#     layover: Layover | None = None

#     # def uuid5(self) -> UUID:
#     #     return self.report.source.uuid5()


# class Trip(BaseModel):
#     uuid: UUID
#     header: TripHeader
#     dutyperiods: list[DutyPeriod]
#     footer: TripFooter | None = None
#     calendar_only: CalendarOnly | None = None
#     calendar_entries: list[str] = []

#     # def uuid5(self) -> UUID:
#     #     return self.header.uuid5()


# class Page(BaseModel):
#     uuid: UUID
#     page_header_1: PageHeader1
#     page_header_2: PageHeader2 | None = None
#     base_equipment: BaseEquipment | None = None
#     page_footer: PageFooter | None = None
#     trips: list[Trip]

#     def uuid5(self) -> UUID:
#         return self.page_header_1.source.uuid5()


# class BidPackage(BaseModel):
#     uuid: UUID
#     source: HashedFile | None
#     pages: list[Page]

#     def default_file_name(self) -> str:
#         assert self.pages[0].page_footer is not None
#         return (
#             f"{self.pages[0].page_footer.effective}_{self.pages[0].page_footer.base}"
#             f"_raw_{self.uuid}.json"
#         )

#     def uuid5(self) -> UUID:
#         if self.source:
#             uuid_seed = self.source.file_hash
#         else:
#             uuid_seed = "None"
#         return uuid5(BIDPACKAGE_DNS, uuid_seed)

#     def walk_trips(self) -> Iterable[Trip]:
#         for page in self.pages:
#             for trip in page.trips:
#                 yield trip

#     def __eq__(self, __value: object) -> bool:
#         if isinstance(__value, BidPackage):
#             if self.source != __value.source:
#                 return False
#             return (self.uuid, self.pages) == (__value.uuid, __value.pages)
#         return super().__eq__(__value)
