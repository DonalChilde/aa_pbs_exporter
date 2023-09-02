from collections.abc import Generator
from pathlib import Path
from typing import Any, TypedDict
from uuid import UUID

from aa_pbs_exporter.pbs_2022_01.helpers.serialize_json import SerializeJson
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    ParseResult,
)

# TODO define bid package metadata


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


class Metadata(TypedDict):
    source: dict[str, str]


class BidPackage(TypedDict):
    uuid: str
    metadata: Metadata | None
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
        for layover in self.layovers():
            self._lookup[layover["uuid"]] = layover

    def lookup(self, uuid: UUID):
        # TODO catch missing uuids
        if not self._lookup:
            self._init_lookup()
        return self._lookup[str(uuid)]

    def pages(self) -> Generator[Page, None, None]:
        for page in self.package["pages"]:
            yield page

    def trips(self, page: Page | None) -> Generator[Trip, None, None]:
        if page is None:
            for page_a in self.pages():
                for trip in page_a["trips"]:
                    yield trip
        else:
            for trip in page["trips"]:
                yield trip

    def dutyperiods(self, trip: Trip | None) -> Generator[DutyPeriod, None, None]:
        if trip is None:
            for trip_a in self.trips(None):
                for dutyperiod in trip_a["dutyperiods"]:
                    yield dutyperiod
        else:
            for dutyperiod in trip["dutyperiods"]:
                yield dutyperiod

    def flights(self, dutyperiod: DutyPeriod | None) -> Generator[Flight, None, None]:
        if dutyperiod is None:
            for dutyperiod_a in self.dutyperiods(None):
                for flight in dutyperiod_a["flights"]:
                    yield flight
        else:
            for flight in dutyperiod["flights"]:
                yield flight

    def layovers(self) -> Generator[Layover, None, None]:
        for dutyperiod_a in self.dutyperiods(None):
            layover = dutyperiod_a.get("layover", None)
            if layover is None:
                continue
            yield layover

    @classmethod
    def default_file_name(cls, source: Path, bid_package: BidPackage) -> str:
        extracted_stub = "-extracted.txt"
        source_file = source.name
        if source_file.endswith(extracted_stub):
            source_file_stub = source_file.removesuffix(extracted_stub)
        else:
            source_file_stub = source.stem
        hash_stub = ""
        if bid_package["metadata"] is not None:
            source_metadata = bid_package["metadata"].get("source", None)
            if source_metadata is not None:
                hash_stub = f'-{source_metadata.get("hash", "hash_missing")}'
        return f"{source_file_stub}{hash_stub}-collated.json"


class Stats:
    # TODO usd this class to generate stats
    pass


def save_json(
    file_out: Path, bid_package: BidPackage, overwrite: bool = False, indent: int = 2
):
    serializer = SerializeJson[BidPackage](data_type_name="collated.BidPackage")
    serializer.save_json(
        file_out=file_out, data=bid_package, overwrite=overwrite, indent=indent
    )


def load_json(file_in: Path) -> BidPackage:
    serializer = SerializeJson[BidPackage](data_type_name="collated.BidPackage")
    data = serializer.load_json(file_in=file_in)
    return data
