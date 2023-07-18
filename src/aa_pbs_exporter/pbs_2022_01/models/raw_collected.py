from typing import Any, Iterator, TypedDict
from uuid import UUID

from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    ParseResult,
)


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


class PackageBrowser:
    def __init__(self, package: BidPackage):
        self.package = package
        self._lookup: dict[str, Any] = {}

    def _init_lookup(self):
        for page in self.pages():
            self._lookup[page["uuid"]] = page
        for trip in self.trips(None):
            self._lookup[trip["uuid"]] = trip
        for dutyperiod in self.dutyperiods(None):
            self._lookup[dutyperiod["uuid"]] = dutyperiod
        for flight in self.flights(None):
            self._lookup[flight["uuid"]] = flight
        for layover in self.layovers(None):
            if layover is not None:
                self._lookup[layover["uuid"]] = layover

    def lookup(self, uuid: UUID):
        # TODO catch missing uuids
        if not self._lookup:
            self._init_lookup()
        return self._lookup[str(uuid)]

    def pages(
        self,
    ) -> Iterator[Page]:
        for page in self.package["pages"]:
            yield page

    def trips(self, page: Page | None) -> Iterator[Trip]:
        if page is None:
            for page_a in self.pages():
                for trip in page_a["trips"]:
                    yield trip
        else:
            for trip in page["trips"]:
                yield trip

    def dutyperiods(self, trip: Trip | None) -> Iterator[DutyPeriod]:
        if trip is None:
            for trip_a in self.trips(None):
                for dutyperiod in trip_a["dutyperiods"]:
                    yield dutyperiod
        else:
            for dutyperiod in trip["dutyperiods"]:
                yield dutyperiod

    def flights(self, dutyperiod: DutyPeriod | None) -> Iterator[Flight]:
        if dutyperiod is None:
            for dutyperiod_a in self.dutyperiods(None):
                for flight in dutyperiod_a["flights"]:
                    yield flight
        else:
            for flight in dutyperiod["flights"]:
                yield flight

    def layovers(self, dutyperiod: DutyPeriod | None) -> Iterator[Layover | None]:
        if dutyperiod is None:
            for dutyperiod_a in self.dutyperiods(None):
                yield dutyperiod_a.get("layover", None)
        else:
            yield dutyperiod.get("layover", None)
