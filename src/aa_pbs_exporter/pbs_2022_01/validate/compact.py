import logging
from datetime import timedelta
from io import TextIOWrapper
from pathlib import Path
from time import perf_counter_ns
import traceback
from typing import Self, cast
from uuid import UUID

from aa_pbs_exporter.pbs_2022_01.helpers import elapsed
from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
from aa_pbs_exporter.pbs_2022_01.models import collated
from aa_pbs_exporter.pbs_2022_01.models import compact
from aa_pbs_exporter.pbs_2022_01.models import parsed
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.string.indent import indent
from aa_pbs_exporter.pbs_2022_01.validate.validation_error import ValidationError

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
"""
TODO

  - Add validation error counter/tracker
  - some how track current location for output in validation error message
    - eg. page\n\ttrip\n\tdutyperiod.
    - store them in class var? self.page_loc,self.trip_loc?
    - functions to return consistant location messages for reuse in trans and validation
    - only generate location message when there is an error?
    
  
"""


class CompactValidator:
    def __init__(
        self,
        debug_file: Path | None = None,
    ) -> None:
        self.debug_file = debug_file
        self.debug_fp: TextIOWrapper | None = None
        self.browser: collated.PackageBrowser
        self.checks = Checks(debug_fp=None)
        self.validation_errors: list[ValidationError] = []

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="a", encoding="utf-8")
            self.checks.debug_fp = self.debug_fp

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
        collated_package: collated.BidPackage,
        compact_package: compact.BidPackage,
    ) -> list[ValidationError]:
        try:
            self._validate(
                collected_package=collated_package, compact_package=compact_package
            )
            self.validation_errors.extend(self.checks.validation_errors)
            return self.validation_errors
        except Exception as error:
            logger.exception("Unexpected error during validation.")
            self.report_error("".join(traceback.format_exception(error)), uuid=None)
            raise error

    def _validate(
        self,
        collected_package: collated.BidPackage,
        compact_package: compact.BidPackage,
    ):
        start = perf_counter_ns()
        self.browser = collated.PackageBrowser(collected_package)
        self.validate_package(
            collected_package=collected_package, compact_package=compact_package
        )
        end = perf_counter_ns()
        self.debug_write(
            f"Validation complete in {elapsed.nanos_to_seconds(start,end):4f} seconds."
        )

    def validate_package(
        self,
        collected_package: collated.BidPackage,
        compact_package: compact.BidPackage,
    ):
        self.debug_write(
            f"********** Validating compact bid package. "
            f"uuid={compact_package.uuid} **********\n",
            Level.PKG,
        )
        page_count = len(compact_package.pages)
        for idx, page in enumerate(compact_package.pages, start=1):
            self.debug_write(
                f"Validating page {page.number}, {idx} of {page_count} "
                f"uuid={page.uuid}",
                Level.PAGE,
            )
            self.validate_page(self.browser.lookup(page.uuid), page)

    def validate_page(
        self,
        collected_page: collated.Page,
        compact_page: compact.Page,
    ):
        self.checks.trips_on_page(compact_page=compact_page)
        trip_count = len(compact_page.trips)
        for trip_idx, trip in enumerate(compact_page.trips, start=1):
            self.debug_write(
                f"Validating trip {trip.number}, {trip_idx} of {trip_count} "
                f"uuid={trip.uuid}",
                Level.TRIP,
            )
            self.validate_trip(self.browser.lookup(trip.uuid), trip)

    def validate_trip(
        self,
        collected_trip: collated.Trip,
        compact_trip: compact.Trip,
    ):
        self.checks.ops_vs_date_count(
            collected_trip=collected_trip, compact_trip=compact_trip
        )
        self.checks.trip_block_time(compact_trip=compact_trip)
        self.checks.trip_positions(compact_trip=compact_trip)
        self.checks.trip_total_pay(compact_trip=compact_trip)
        self.checks.dutyperiod_index(compact_trip=compact_trip)
        self.checks.layover_present(compact_trip=compact_trip)
        dp_count = len(compact_trip.dutyperiods)
        for dp_idx, dutyperiod in enumerate(compact_trip.dutyperiods):
            self.debug_write(
                f"Validating dutyperiod {dp_idx} of {dp_count} "
                f"uuid={dutyperiod.uuid}",
                Level.DP,
            )
            self.validate_dutyperiod(self.browser.lookup(dutyperiod.uuid), dutyperiod)

    def validate_dutyperiod(
        self,
        collected_dutyperiod: collated.DutyPeriod,
        compact_dutyperiod: compact.DutyPeriod,
    ):
        self.checks.dutyperiod_block(compact_dutyperiod=compact_dutyperiod)
        self.checks.dutyperiod_total_pay(compact_dutyperiod=compact_dutyperiod)
        flt_count = len(compact_dutyperiod.flights)
        for flt_idx, flight in enumerate(compact_dutyperiod.flights):
            self.debug_write(
                f"Validating flight {flt_idx} of {flt_count} uuid={flight.uuid}",
                Level.FLT,
            )
            self.validate_flight(self.browser.lookup(flight.uuid), flight)
        if compact_dutyperiod.layover is not None:
            self.debug_write(
                f"Validating layover uuid={compact_dutyperiod.layover.uuid}",
                Level.DP,
            )
            self.validate_layover(
                self.browser.lookup(compact_dutyperiod.layover.uuid),
                compact_dutyperiod.layover,
            )

    def validate_flight(
        self, collected_flight: collated.Flight, compact_flight: compact.Flight
    ):
        pass

    def validate_layover(
        self,
        collected_layover: collated.Layover | None,
        compact_layover: compact.Layover | None,
    ):
        pass


def validate_compact_bid_package(
    raw_bid_package: collated.BidPackage,
    compact_bid_package: compact.BidPackage,
    debug_file: Path | None = None,
):
    with CompactValidator(debug_file=debug_file) as validator:
        validator.validate(
            collated_package=raw_bid_package, compact_package=compact_bid_package
        )


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

    def ops_vs_date_count(
        self, collected_trip: collated.Trip, compact_trip: compact.Trip
    ):
        header_data = cast(parsed.TripHeader, collected_trip["header"]["parsed_data"])
        ops = int(header_data["ops_count"])
        date_count = len(compact_trip.start_dates)
        if ops != date_count:
            msg = (
                f"Ops count for raw trips {ops} "
                f"does not match start date count {date_count} "
                f"for compact trip {compact_trip.number}. "
            )
            self.report_error(msg, compact_trip.uuid, Level.TRIP + 1)

    def trips_on_page(
        self,
        compact_page: compact.Page,
    ):
        if len(compact_page.trips) < 1:
            msg = (
                f"No trips found on compact page ref={compact_page.number}. "
                "Were they all prior month trips?"
            )
            self.report_error(msg, compact_page.uuid, Level.PAGE + 1)

    def trip_block_time(self, compact_trip: compact.Trip):
        sum_block = timedelta()
        for dutyperiod in compact_trip.dutyperiods:
            sum_block += dutyperiod.block
        if sum_block != compact_trip.block:
            msg = (
                f"Sum of block {sum_block} does not match parsed "
                f"block {compact_trip.block} "
                f"for compact trip {compact_trip.number}."
            )
            self.report_error(msg, compact_trip.uuid, Level.TRIP + 1)

    def trip_total_pay(self, compact_trip: compact.Trip):
        sum_total_pay = compact_trip.synth + compact_trip.block
        if sum_total_pay != compact_trip.total_pay:
            msg = (
                f"Sum of synth and block ({compact_trip.synth} + {compact_trip.block} "
                f"= {sum_total_pay}) "
                f"does not match parsed total pay {compact_trip.total_pay} "
                f"for compact trip {compact_trip.number}. "
            )
            self.report_error(msg, compact_trip.uuid, Level.TRIP + 1)

    def trip_positions(self, compact_trip: compact.Trip):
        if not compact_trip.positions:
            msg = f"No positions found " f"for compact trip {compact_trip.number}. "
            self.report_error(msg, compact_trip.uuid, Level.TRIP + 1)

    def layover_present(self, compact_trip: compact.Trip):
        last_index = len(compact_trip.dutyperiods) - 1
        for idx, dutyperiod in enumerate(compact_trip.dutyperiods):
            if dutyperiod.layover is None and not idx == last_index:
                msg = (
                    f"Layover missing from compact trip {compact_trip.number}, "
                    f"dutyperiod:{idx+1}"
                )
                self.report_error(msg, compact_trip.uuid, Level.TRIP + 1)

        if compact_trip.dutyperiods[last_index].layover is not None:
            msg = (
                f"The layover for the last dutyperiod of compact trip "
                f"{compact_trip.number} is not None."
            )
            self.report_error(msg, compact_trip.uuid, Level.TRIP + 1)

    def dutyperiod_index(self, compact_trip: compact.Trip):
        for dp_idx, dutyperiod in enumerate(compact_trip.dutyperiods, start=1):
            if dp_idx != dutyperiod.idx:
                msg = (
                    f"Code idx {dp_idx} does not match parsed dutyperiod index "
                    f"{dutyperiod.idx}. "
                )
                self.report_error(msg, dutyperiod.uuid, Level.DP + 1)

            for flt_idx, flight in enumerate(dutyperiod.flights, start=1):
                if dp_idx != flight.dp_idx:
                    msg = (
                        f"Code idx {flt_idx} does not match parsed dutyperiod idx for "
                        f"flight index {flight.dp_idx}. "
                    )
                    self.report_error(msg, flight.uuid, Level.FLT + 1)

                if flt_idx != flight.idx:
                    msg = (
                        f"Code idx {flt_idx} does not match parsed "
                        "flight idx {flight.idx}. "
                    )
                    self.report_error(msg, flight.uuid, Level.FLT + 1)

    def dutyperiod_block(self, compact_dutyperiod: compact.DutyPeriod):
        sum_block = timedelta()
        for flight in compact_dutyperiod.flights:
            sum_block += flight.block
        if sum_block != compact_dutyperiod.block:
            msg = (
                f"Sum of block {sum_block} does not match parsed "
                f"block {compact_dutyperiod.block} for compact dutyperiod. "
                f"dp_idx={compact_dutyperiod.idx} "
            )
            self.report_error(msg, compact_dutyperiod.uuid, Level.DP + 1)

    def dutyperiod_total_pay(self, compact_dutyperiod: compact.DutyPeriod):
        sum_total_pay = compact_dutyperiod.synth + compact_dutyperiod.block
        if sum_total_pay != compact_dutyperiod.total_pay:
            msg = (
                f"Sum of synth and block ({compact_dutyperiod.synth} + "
                f"{compact_dutyperiod.block} = {sum_total_pay}) "
                f"Does not match parsed total {compact_dutyperiod.total_pay} "
                f"dp_idx={compact_dutyperiod.idx} "
            )
            self.report_error(msg, compact_dutyperiod.uuid, Level.DP + 1)
