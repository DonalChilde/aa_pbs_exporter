import logging
from datetime import timedelta
from io import TextIOWrapper
from pathlib import Path
from time import perf_counter_ns
import traceback
from typing import Self
from uuid import UUID

from aa_pbs_exporter.pbs_2022_01.helpers.compare_time import compare_time
from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
from aa_pbs_exporter.pbs_2022_01.helpers.length import length
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.pbs_2022_01.validate.validation_error import ValidationError
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.string.indent import indent
from aa_pbs_exporter.pbs_2022_01.helpers import elapsed


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

TIME = "%H%M"
ERROR = "expanded.validation.error"
STATUS = "expanded.validation.status"
DEBUG = "expanded.validation.debug"


class ExpandedValidator:
    def __init__(
        self,
        debug_file: Path | None = None,
    ) -> None:
        self.debug_file = debug_file
        self.debug_fp: TextIOWrapper | None = None
        self.compact_browser: compact.PackageBrowser
        self.expanded_browser: expanded.PackageBrowser
        self.checks: Checks
        self.validation_errors: list[ValidationError] = []

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="a", encoding="utf-8")
            self.checks = Checks(debug_fp=self.debug_fp)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.debug_write(f"Found {len(self.validation_errors)} errors.")
        self.debug_write("\n".join([str(x) for x in self.validation_errors]), 0)
        if self.debug_fp is not None:
            self.debug_fp.close()

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def report_error(self, msg: str, uuid: UUID | None, indent_level: int = 0):
        error = ValidationError(msg=msg, uuid=uuid)
        self.validation_errors.append(error)
        self.debug_write(str(error), indent_level=indent_level)

    def validate(
        self,
        compact_bid: compact.BidPackage,
        expanded_bid: expanded.BidPackage,
    ) -> list[ValidationError]:
        try:
            self._validate(compact_bid=compact_bid, expanded_bid=expanded_bid)
            self.validation_errors.extend(self.checks.validation_errors)
            return self.validation_errors
        except Exception as error:
            logger.exception("Unexpected error during translation.")
            self.report_error("".join(traceback.format_exception(error)), uuid=None)
            raise error

    def _validate(
        self,
        compact_bid: compact.BidPackage,
        expanded_bid: expanded.BidPackage,
    ):
        start = perf_counter_ns()
        self.compact_browser = compact.PackageBrowser(package=compact_bid)
        self.expanded_browser = expanded.PackageBrowser(expanded_bid)
        self.validate_bid_package(compact_bid, expanded_bid)
        end = perf_counter_ns()
        self.debug_write(
            f"Validation complete in {elapsed.nanos_to_seconds(start,end):4f} seconds."
        )

    def validate_bid_package(
        self,
        compact_bid: compact.BidPackage,
        expanded_bid: expanded.BidPackage,
    ):
        _ = compact_bid
        self.debug_write(
            f"********** Validating expanded bid package. "
            f"uuid={expanded_bid.uuid} **********",
            Level.PKG,
        )
        self.checks.pages_in_bid_package(bid_package=expanded_bid)
        trip_count = length(self.expanded_browser.trips(None))
        self.checks.trips_in_bid_package(
            bid_package=expanded_bid, trip_count=trip_count
        )
        page_count = len(expanded_bid.pages)
        for page_idx, page in enumerate(expanded_bid.pages, start=1):
            self.debug_write(
                f"Validating page {page.number}, {page_idx} of {page_count}",
                Level.PAGE,
            )
            compact_page = self.compact_browser.lookup(page.uuid)
            self.validate_page(compact_page, page)

    def validate_page(
        self,
        compact_page: compact.Page,
        expanded_page: expanded.Page,
    ):
        # page validations here
        trip_count = len(expanded_page.trips)
        for trip_idx, trip in enumerate(expanded_page.trips, start=1):
            self.debug_write(
                f"Validating trip {trip.number}, {trip_idx} of {trip_count} on page "
                f"{expanded_page.number}, start={trip.start}",
                Level.TRIP,
            )
            compact_trip = self.compact_browser.lookup(trip.compact_uuid)
            self.validate_trip(compact_trip, trip)

    def validate_trip(
        self,
        compact_trip: compact.Trip,
        expanded_trip: expanded.Trip,
    ):
        _ = compact_trip
        self.checks.check_trip_tafb(expanded_trip)
        self.checks.check_trip_length(expanded_trip)
        self.checks.check_trip_end(expanded_trip)
        dp_count = len(expanded_trip.dutyperiods)
        for dp_idx, dutyperiod in enumerate(expanded_trip.dutyperiods, start=1):
            self.debug_write(
                f"Validating dutyperiod {dp_idx} of {dp_count} for trip "
                f"{expanded_trip.number}",
                Level.DP,
            )
            compact_dutyperiod = self.compact_browser.lookup(dutyperiod.compact_uuid)
            self.validate_dutyperiod(
                compact_dutyperiod, dutyperiod, expanded_trip.number
            )

    def validate_dutyperiod(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        trip_number: str,
    ):
        self.checks.check_report_times(
            compact_dutyperiod, expanded_dutyperiod, trip_number
        )
        self.checks.check_release_times(
            compact_dutyperiod, expanded_dutyperiod, trip_number
        )
        self.checks.check_dutytime(expanded_dutyperiod, trip_number)
        flight_count = len(expanded_dutyperiod.flights)
        for flt_idx, flight in enumerate(expanded_dutyperiod.flights, start=1):
            self.debug_write(
                f"Validating flight {flight.number}, {flt_idx} of " f"{flight_count}",
                Level.FLT,
            )
            compact_flight = self.compact_browser.lookup(flight.compact_uuid)
            self.validate_flight(compact_flight, flight, trip_number)

    def validate_flight(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        trip_number: str,
    ):
        self.checks.check_departure(compact_flight, expanded_flight, trip_number)
        self.checks.check_arrival(compact_flight, expanded_flight, trip_number)
        self.checks.check_flight_time(expanded_flight, trip_number)

    def validate_layover(
        self,
        compact_layover: compact.Layover,
        expanded_layover: expanded.Layover,
    ):
        pass

    def validate_hotel(
        self,
        conpact_hotel: compact.Hotel,
        expanded_hotel: expanded.Hotel,
    ):
        pass

    def validate_transportation(
        self,
        compact_transportation: compact.Transportation,
        expanded_transportation: expanded.Transportation,
    ):
        pass


class Checks:
    def __init__(self, debug_fp: TextIOWrapper | None = None) -> None:
        self.debug_fp = debug_fp
        self.validation_errors: list[ValidationError] = []

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def report_error(self, msg: str, uuid: UUID | None, indent_level: int = 0):
        error = ValidationError(msg=msg, uuid=uuid)
        self.validation_errors.append(error)
        self.debug_write(str(error), indent_level=indent_level)

    def check_trip_length(self, expanded_trip: expanded.Trip):
        total = timedelta()
        for dutyperiod in expanded_trip.dutyperiods:
            duration = dutyperiod.release.utc_date - dutyperiod.report.utc_date
            total += duration
            if dutyperiod.layover is not None:
                total += dutyperiod.layover.odl
        if total != expanded_trip.tafb:
            msg = (
                f"Calculated trip length {total} does not match "
                f"parsed trip length {expanded_trip.tafb} for trip {expanded_trip.number} "
                f"compact_uuid: {expanded_trip.compact_uuid} "
            )
            self.report_error(msg, expanded_trip.uuid, Level.TRIP + 1)

    def check_trip_tafb(self, expanded_trip: expanded.Trip):
        last_release = expanded_trip.dutyperiods[-1].release.utc_date
        trip_tafb = last_release - expanded_trip.start.utc_date
        if trip_tafb != expanded_trip.tafb:
            msg = (
                f"Calculated trip tafb {trip_tafb} does not match "
                f"parsed trip tafb {expanded_trip.tafb} for trip {expanded_trip.number} "
                f"compact_uuid: {expanded_trip.compact_uuid} "
            )
            self.report_error(msg, expanded_trip.uuid, Level.TRIP + 1)

    def check_trip_end(self, expanded_trip: expanded.Trip):
        last_release = expanded_trip.dutyperiods[-1].release
        if last_release != expanded_trip.end:
            msg = (
                f"Computed end of trip {expanded_trip.end!r} does not match last "
                f"dutyperiod release {last_release!r} for trip {expanded_trip.number} "
                f"compact_uuid: {expanded_trip.compact_uuid} "
            )
            self.report_error(msg, expanded_trip.uuid, Level.TRIP + 1)

    def check_dutytime(
        self,
        expanded_dutyperiod: expanded.DutyPeriod,
        trip_number: str,
    ):
        dutytime = (
            expanded_dutyperiod.release.utc_date - expanded_dutyperiod.report.utc_date
        )
        if dutytime != expanded_dutyperiod.duty:
            msg = (
                f"Calculated dutytime {dutytime} does not match "
                f"parsed dutytime {expanded_dutyperiod.duty} "
                f"trip number: {trip_number} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} "
                f"\n\trelease:{expanded_dutyperiod.release}"
                f"\n\treport:{expanded_dutyperiod.report}"
            )
            self.report_error(msg, expanded_dutyperiod.uuid, Level.DP + 1)

    def check_arrival(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        trip_number: str,
    ):
        arrival_time = expanded_flight.arrival.localize().time()
        if not compare_time(
            arrival_time,
            compact_flight.arrival.lcl.time,
            ignore_tz=True,
        ):
            msg = (
                f"Arrival times do not match for flight {expanded_flight.number}. "
                f"compact: {compact_flight.arrival.lcl!r}, "
                f"expanded: {arrival_time!r}. "
                f"trip number: {trip_number} "
                f"compact_uuid: {expanded_flight.compact_uuid} "
            )
            self.report_error(msg, expanded_flight.uuid, Level.FLT + 1)

    def check_departure(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        trip_number: str,
    ):
        departure_time = expanded_flight.departure.localize().time()
        if not compare_time(
            departure_time,
            compact_flight.departure.lcl.time,
            ignore_tz=True,
        ):
            msg = (
                f"Departure times do not match for flight {expanded_flight.number}. "
                f"compact: {compact_flight.departure.lcl!r}, "
                f"expanded: {departure_time!r}. "
                f"trip number: {trip_number} "
                f"compact_uuid: {expanded_flight.compact_uuid} "
            )
            self.report_error(msg, expanded_flight.uuid, Level.FLT + 1)

    def check_flight_time(
        self,
        expanded_flight: expanded.Flight,
        trip_number: str,
    ):
        flight_time = (
            expanded_flight.arrival.utc_date - expanded_flight.departure.utc_date
        )
        if expanded_flight.deadhead:
            if flight_time != expanded_flight.synth:
                msg = (
                    f"Flight time {flight_time} does not match synth time "
                    f"{expanded_flight.synth} on deadhead flight {expanded_flight.number}. "
                    f"trip number: {trip_number} "
                    f"compact_uuid: {expanded_flight.compact_uuid} "
                )
                self.report_error(msg, expanded_flight.uuid, Level.FLT + 1)
            return
        if flight_time != expanded_flight.block:
            msg = (
                f"Flight time {flight_time} does not match block time "
                f"{expanded_flight.block} on flight {expanded_flight.number}. "
                f"trip number: {trip_number} "
                f"compact_uuid: {expanded_flight.compact_uuid} "
                f"\n\tdeparture: {expanded_flight.departure_station} {expanded_flight.departure}"
                f"\n\tarrival: {expanded_flight.arrival_station} {expanded_flight.arrival}"
            )
            self.report_error(msg, expanded_flight.uuid, Level.FLT + 1)

    def check_report_times(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        trip_number: str,
    ):
        report_time = expanded_dutyperiod.report.localize().time()
        if not compare_time(
            report_time,
            compact_dutyperiod.report.lcl.time,
            ignore_tz=True,
        ):
            msg = (
                f"Report times do not match. "
                f"compact: {compact_dutyperiod.report}, "
                f"expanded: {expanded_dutyperiod.report}. "
                f"trip number: {trip_number} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} "
            )
            self.report_error(msg, expanded_dutyperiod.uuid, Level.DP + 1)

    def check_release_times(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        trip_number: str,
    ):
        release_time = expanded_dutyperiod.release.localize().time()
        if not compare_time(
            release_time,
            compact_dutyperiod.release.lcl.time,
            ignore_tz=True,
        ):
            msg = (
                f"Release times do not match. "
                f"compact: {compact_dutyperiod.release.lcl!r}, "
                f"expanded: {release_time!r}. "
                f"trip number: {trip_number} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} "
            )
            self.report_error(msg, expanded_dutyperiod.uuid, Level.DP + 1)

    def pages_in_bid_package(self, bid_package: expanded.BidPackage):
        if not bid_package.pages:
            msg = "Expanded bid package bid has no pages."
            self.report_error(msg, bid_package.uuid, Level.PKG + 1)

    def trips_in_bid_package(self, bid_package: expanded.BidPackage, trip_count: int):
        if trip_count < 1:
            msg = "No trips found in expanded bid package."
            self.report_error(msg, bid_package.uuid, Level.PKG + 1)
