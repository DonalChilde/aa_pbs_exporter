from io import TextIOWrapper
from pathlib import Path
import traceback
from typing import Self
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
)
from aa_pbs_exporter.pbs_2022_01.models import collated

from aa_pbs_exporter.snippets.string.indent import indent
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CollatedValidator:
    def __init__(
        self,
        debug_file: Path | None = None,
    ) -> None:
        self.debug_file = debug_file
        self.debug_fp: TextIOWrapper | None = None
        self.checks = Checks(debug_fp=None)

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="a", encoding="utf-8")
            self.checks.debug_fp = self.debug_fp

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug_fp is not None:
            self.debug_fp.close()

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def validate(
        self, parse_results: CollectedParseResults, bid_package: collated.BidPackage
    ):
        try:
            return self._validate(parse_results=parse_results, bid_package=bid_package)
        except Exception as error:
            logger.exception("Unexpected error during validation.")
            self.debug_write("".join(traceback.format_exception(error)), 0)
            raise error

    def _validate(
        self, parse_results: CollectedParseResults, bid_package: collated.BidPackage
    ):
        pass


class Checks:
    def __init__(self, debug_fp: TextIOWrapper | None = None) -> None:
        self.debug_fp = debug_fp

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)


def validate_collated_bid_package(
    parse_results: CollectedParseResults,
    bid_package: collated.BidPackage,
    debug_file: Path | None,
):
    # TODO compare calendar entries that are mumbers, with ops count
    with CollatedValidator(debug_file=debug_file) as validator:
        validator.validate(parse_results=parse_results, bid_package=bid_package)


# from io import TextIOWrapper
# import logging

# from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
# from aa_pbs_exporter.pbs_2022_01.models import raw_td as raw
# from aa_pbs_exporter.snippets.string.indent import indent


# logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())

# ERROR = "raw.validation.error"
# STATUS = "raw.validation.status"
# DEBUG = "raw.validation.debug"


# class RawValidator:
#     def __init__(
#         self,
#         debug_fp: TextIOWrapper | None = None,
#     ) -> None:
#         self.debug_fp = debug_fp

#     def debug_write(self, value: str, indent_level: int = 0):
#         if self.debug_fp is not None:
#             print(indent(value, indent_level), file=self.debug_fp)

#     def validate(self, bid_package: raw.BidPackage, ctx: dict | None):
#         self.debug_write(
#             f"********** Validating raw bid package. uuid={bid_package.uuid} **********"
#         )

#         self.validate_bid_package(bid_package, ctx)
#         page_count = len(bid_package.pages)
#         for page_idx, page in enumerate(bid_package.pages, start=1):
#             self.debug_write(f"Validating page {page_idx} of {page_count}", Level.PAGE)
#             trip_count = len(page.trips)
#             self.validate_page(page, ctx)
#             for trip_idx, trip in enumerate(page.trips, start=1):
#                 self.debug_write(
#                     f"Validating trip {trip.header.number}, {trip_idx} of {trip_count}",
#                     Level.TRIP,
#                 )
#                 self.validate_trip(trip, ctx)
#                 dp_count = len(trip.dutyperiods)
#                 for dp_idx, dutyperiod in enumerate(trip.dutyperiods, start=1):
#                     self.debug_write(
#                         f"Validating dutyperiod {dp_idx} of {dp_count}", Level.DP
#                     )
#                     self.validate_dutyperiod(dutyperiod, ctx)
#                     flight_count = len(dutyperiod.flights)
#                     for flt_idx, flight in enumerate(dutyperiod.flights, start=1):
#                         self.debug_write(
#                             f"Validating flight {flight.flight_number}, {flt_idx} of {flight_count}",
#                             Level.FLT,
#                         )
#                         self.validate_flight(flight, ctx)

#     def validate_bid_package(self, bid_package: raw.BidPackage, ctx: dict | None):
#         self.debug_write(f"Validating bid package. uuid={bid_package.uuid}", Level.PKG)
#         self.check_bid_for_empty_properies(bid_package=bid_package, ctx=ctx)

#     def validate_page(self, page: raw.Page, ctx: dict | None):
#         self.check_page_for_empty_properies(page=page, ctx=ctx)

#     def validate_trip(self, trip: raw.Trip, ctx: dict | None):
#         self.check_trip_for_empty_properies(trip=trip, ctx=ctx)

#     def validate_dutyperiod(self, dutyperiod: raw.DutyPeriod, ctx: dict | None):
#         self.check_dutyperiod_for_empty_properies(dutyperiod=dutyperiod, ctx=ctx)

#     def validate_layover(self, layover: raw.Layover, ctx: dict | None):
#         self.check_layover_for_empty_properies(layover, ctx)

#     def validate_flight(self, flight: raw.Flight, ctx: dict | None):
#         pass

#     def check_bid_for_empty_properies(
#         self, bid_package: raw.BidPackage, ctx: dict | None
#     ):
#         if not bid_package.pages:
#             self.debug_write(
#                 f"ERROR: Bid package has no pages. uuid: {bid_package.uuid} "
#                 f"source: {bid_package.source}"
#             )

#     def check_page_for_empty_properies(self, page: raw.Page, ctx: dict | None):
#         if not page.trips:
#             self.debug_write(f"ERROR: Page has no trips. uuid: {page.uuid}")
#         if page.page_header_2 is None:
#             self.debug_write(f"ERROR: Page has no page_header_2. uuid: {page.uuid}")
#         if page.page_footer is None:
#             self.debug_write("ERROR: Page has no page_footer. uuid: {page.uuid}")

#     def check_trip_for_empty_properies(self, trip: raw.Trip, ctx: dict | None):
#         _ = ctx
#         if not trip.dutyperiods:
#             self.debug_write(f"ERROR: Trip has no dutyperiods. uuid: {trip.uuid}")
#         if trip.footer is None:
#             self.debug_write(f"ERROR: Trip has no footer. uuid: {trip.uuid}")

#     def check_dutyperiod_for_empty_properies(
#         self, dutyperiod: raw.DutyPeriod, ctx: dict | None
#     ):
#         _ = ctx
#         if not dutyperiod.flights:
#             self.debug_write(
#                 f"ERROR: Dutyperiod has no flights. uuid: {dutyperiod.uuid}"
#             )
#         if dutyperiod.release is None:
#             self.debug_write(
#                 f"ERROR: Dutyperiod has no release. uuid: {dutyperiod.uuid}"
#             )
#         if dutyperiod.layover is not None:
#             self.check_layover_for_empty_properies(layover=dutyperiod.layover, ctx=ctx)

#     def check_layover_for_empty_properies(self, layover: raw.Layover, ctx: dict | None):
#         _ = ctx
#         assert layover is not None
#         if layover.hotel_info[0].hotel is None:
#             self.debug_write(
#                 f"ERROR: Layover has no primary hotel. uuid: {layover.uuid}"
#             )
