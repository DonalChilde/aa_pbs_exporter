from datetime import timedelta
from io import TextIOWrapper
from pathlib import Path
from typing import Self, cast

from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
from aa_pbs_exporter.pbs_2022_01.models import compact
from aa_pbs_exporter.pbs_2022_01.models import raw_collected as raw_c
from aa_pbs_exporter.pbs_2022_01.models import raw_parsed as raw_p
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.string.indent import indent

"""
TODO

  - move validations over from old code
  - make raw-collected names consistent
  - Make browser for compact and expanded models
  - add a reference to the compact browser
  - refactor validate namespace to remove excess validates
"""


class ValidateCompact:
    def __init__(
        self,
        debug_file: Path | None = None,
    ) -> None:
        self.debug_file = debug_file
        self.debug_fp: TextIOWrapper | None = None
        self.browser: raw_c.PackageBrowser
        self.checks = Checks(debug_fp=None)

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="w", encoding="utf-8")
            self.checks.debug_fp = self.debug_fp

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug_fp is not None:
            self.debug_fp.close()

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def validate(
        self,
        collected_package: raw_c.BidPackage,
        compact_package: compact.BidPackage,
    ):
        self.browser = raw_c.PackageBrowser(collected_package)
        self.validate_package(
            collected_package=collected_package, compact_package=compact_package
        )

    def validate_package(
        self,
        collected_package: raw_c.BidPackage,
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
        collected_page: raw_c.Page,
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
        collected_trip: raw_c.Trip,
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
        collected_dutyperiod: raw_c.DutyPeriod,
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
        self, collected_flight: raw_c.Flight, compact_flight: compact.Flight
    ):
        pass

    def validate_layover(
        self,
        collected_layover: raw_c.Layover | None,
        compact_layover: compact.Layover | None,
    ):
        pass


def validate_compact_bid_package(
    raw_bid_package: raw_c.BidPackage,
    compact_bid_package: compact.BidPackage,
    debug_file: Path | None = None,
):
    with ValidateCompact(debug_file=debug_file) as validator:
        validator.validate(
            collected_package=raw_bid_package, compact_package=compact_bid_package
        )


class Checks:
    def __init__(self, debug_fp: TextIOWrapper | None = None) -> None:
        self.debug_fp = debug_fp

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def ops_vs_date_count(self, collected_trip: raw_c.Trip, compact_trip: compact.Trip):
        header_data = cast(raw_p.TripHeader, collected_trip["header"]["parsed_data"])
        ops = int(header_data["ops_count"])
        date_count = len(compact_trip.start_dates)
        if ops != date_count:
            self.debug_write(
                f"Ops count for raw trips {ops} "
                f"does not match start date count {date_count} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}",
                Level.TRIP + 1,
            )

    def trips_on_page(
        self,
        compact_page: compact.Page,
    ):
        if len(compact_page.trips) < 1:
            self.debug_write(
                f"No trips found on compact page ref={compact_page.number}. "
                f"Were they all prior month trips? uuid: {compact_page.uuid}",
                Level.PAGE + 1,
            )

    def trip_block_time(self, compact_trip: compact.Trip):
        sum_block = timedelta()
        for dutyperiod in compact_trip.dutyperiods:
            sum_block += dutyperiod.block
        if sum_block != compact_trip.block:
            self.debug_write(
                f"Sum of block {sum_block} does not match parsed "
                f"block {compact_trip.block} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}",
                Level.TRIP + 1,
            )

    def trip_total_pay(self, compact_trip: compact.Trip):
        sum_total_pay = compact_trip.synth + compact_trip.block
        if sum_total_pay != compact_trip.total_pay:
            self.debug_write(
                f"Sum of synth and block ({compact_trip.synth} + {compact_trip.block} "
                f"= {sum_total_pay}) "
                f"does not match parsed total pay {compact_trip.total_pay} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}",
                Level.TRIP + 1,
            )

    def trip_positions(self, compact_trip: compact.Trip):
        if not compact_trip.positions:
            self.debug_write(
                f"No positions found "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}",
                Level.TRIP + 1,
            )

    def layover_present(self, compact_trip: compact.Trip):
        last_index = len(compact_trip.dutyperiods) - 1
        for idx, dutyperiod in enumerate(compact_trip.dutyperiods):
            if dutyperiod.layover is None and not idx == last_index:
                self.debug_write(
                    f"Layover missing from compact trip {compact_trip.number}, "
                    f"dutyperiod:{idx+1}"
                    f"uuid: {compact_trip.uuid}",
                    Level.TRIP + 1,
                )
        if compact_trip.dutyperiods[last_index].layover is not None:
            self.debug_write(
                f"The layover for the last dutyperiod of compact trip "
                f"{compact_trip.number} is not None.",
                Level.TRIP + 1,
            )

    def dutyperiod_index(self, compact_trip: compact.Trip):
        for dp_idx, dutyperiod in enumerate(compact_trip.dutyperiods, start=1):
            if dp_idx != dutyperiod.idx:
                self.debug_write(
                    f"Code idx {dp_idx} does not match parsed dutyperiod index "
                    f"{dutyperiod.idx}. "
                    f"uuid:{dutyperiod.uuid}",
                    Level.DP + 1,
                )
            for flt_idx, flight in enumerate(dutyperiod.flights, start=1):
                if dp_idx != flight.dp_idx:
                    self.debug_write(
                        f"Code idx {flt_idx} does not match parsed dutyperiod idx for "
                        f"flight index {flight.dp_idx}. "
                        f"uuid:{flight.uuid}",
                        Level.FLT + 1,
                    )
                if flt_idx != flight.idx:
                    self.debug_write(
                        f"Code idx {flt_idx} does not match parsed flight idx {flight.idx}. "
                        f"uuid:{flight.uuid}",
                        Level.FLT + 1,
                    )

    def dutyperiod_block(self, compact_dutyperiod: compact.DutyPeriod):
        sum_block = timedelta()
        for flight in compact_dutyperiod.flights:
            sum_block += flight.block
        if sum_block != compact_dutyperiod.block:
            self.debug_write(
                f"Sum of block {sum_block} does not match parsed "
                f"block {compact_dutyperiod.block} for compact dutyperiod. "
                f"dp_idx={compact_dutyperiod.idx} "
                f"uuid: {compact_dutyperiod.uuid}",
                Level.DP + 1,
            )

    def dutyperiod_total_pay(self, compact_dutyperiod: compact.DutyPeriod):
        sum_total_pay = compact_dutyperiod.synth + compact_dutyperiod.block
        if sum_total_pay != compact_dutyperiod.total_pay:
            self.debug_write(
                f"Sum of synth and block ({compact_dutyperiod.synth} + "
                f"{compact_dutyperiod.block} = {sum_total_pay}) "
                f"Does not match parsed total {compact_dutyperiod.total_pay} "
                f"dp_idx={compact_dutyperiod.idx} "
                f"uuid: {compact_dutyperiod.uuid}",
                Level.DP + 1,
            )
