from typing import TypedDict

from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    ParseResult,
)


class HotelInfo(TypedDict):
    hotel: ParseResult
    transportation: ParseResult


class Layover(TypedDict):
    uuid: str
    layover: ParseResult
    hotel_info: list[ParseResult]


class Flight(TypedDict):
    uuid: str
    flight: ParseResult


class DutyPeriod(TypedDict):
    uuid: str
    report: ParseResult
    flights: list[Flight]
    release: ParseResult
    layover: Layover


class Trip(TypedDict):
    uuid: str
    header: ParseResult
    dutyperiods: list[DutyPeriod]
    footer: ParseResult
    calendar_only: ParseResult
    calendar_entries: list[str]


class Page(TypedDict):
    uuid: str
    page_header_1: ParseResult
    page_header_2: ParseResult
    base_equipment: ParseResult
    page_footer: ParseResult
    trips: list[Trip]


class BidPackage(TypedDict):
    uuid: str
    metadata: dict
    pages: list[Page]


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
