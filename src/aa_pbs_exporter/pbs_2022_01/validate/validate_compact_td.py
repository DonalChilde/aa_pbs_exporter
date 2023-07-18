from io import TextIOWrapper
from pathlib import Path
from typing import Self

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

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="w", encoding="utf-8")

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
        self.debug_write(
            f"********** Validating compact bid package. "
            f"uuid={compact_package.uuid} **********\n",
            Level.PKG,
        )
        self.browser = raw_c.PackageBrowser(collected_package)
        page_count = len(compact_package.pages)
        for idx, page in enumerate(compact_package.pages, start=1):
            self.debug_write(
                f"Validating page {page.number}, {idx} of {page_count}",
                Level.PAGE,
            )
            self.validate_page(self.browser.lookup(page.uuid), page)

    def validate_package(
        self,
        collected_package: raw_c.BidPackage,
        compact_package: compact.BidPackage,
    ):
        pass

    def validate_page(
        self,
        collected_page: raw_c.Page,
        compact_page: compact.Page,
    ):
        for trip in compact_page.trips:
            self.validate_trip(self.browser.lookup(trip.uuid), trip)

    def validate_trip(
        self,
        collected_trip: raw_c.Trip,
        compact_trip: compact.Trip,
    ):
        for dutyperiod in compact_trip.dutyperiods:
            self.validate_dutyperiod(self.browser.lookup(dutyperiod.uuid), dutyperiod)

    def validate_dutyperiod(
        self,
        collected_dutyperiod: raw_c.DutyPeriod,
        compact_dutyperiod: compact.DutyPeriod,
    ):
        for flight in compact_dutyperiod.flights:
            self.validate_flight(self.browser.lookup(flight.uuid), flight)
        self.validate_layover(
            collected_dutyperiod.get("layover", None), compact_dutyperiod.layover
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
