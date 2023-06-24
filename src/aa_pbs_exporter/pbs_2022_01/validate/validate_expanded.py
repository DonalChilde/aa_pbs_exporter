import logging
from datetime import timedelta
from io import TextIOWrapper
import time

from aa_pbs_exporter.pbs_2022_01.helpers.compare_time import compare_time
from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
from aa_pbs_exporter.pbs_2022_01.helpers.length import length
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
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
        debug_fp: TextIOWrapper | None = None,
    ) -> None:
        self.debug_fp = debug_fp

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def validate(
        self,
        compact_bid: compact.BidPackage,
        expanded_bid: expanded.BidPackage,
        ctx: dict | None,
    ):
        self.debug_write(
            f"********** Validating expanded bid package. "
            f"uuid={expanded_bid.uuid} **********",
            Level.PKG,
        )
        self.validate_bid_package(compact_bid, expanded_bid, ctx)
        page_lookup = {x.uuid: x for x in compact_bid.pages}
        page_count = len(expanded_bid.pages)
        for page_idx, page in enumerate(expanded_bid.pages, start=1):
            self.debug_write(
                f"Validating page {page.number}, {page_idx} of {page_count}",
                Level.PAGE,
            )
            compact_page = page_lookup[page.uuid]
            self.validate_page(compact_page, page, ctx)
            trip_lookup = {x.uuid: x for x in compact_page.trips}
            trip_count = len(page.trips)
            for trip_idx, trip in enumerate(page.trips, start=1):
                self.debug_write(
                    f"Validating trip {trip.number}, {trip_idx} of {trip_count} on page "
                    f"{page.number}, start={trip.start}",
                    Level.TRIP,
                )
                compact_trip = trip_lookup[trip.compact_uuid]
                self.validate_trip(compact_trip, trip, ctx)
                dutyperiod_lookup = {x.uuid: x for x in compact_trip.dutyperiods}
                dp_count = len(trip.dutyperiods)
                for dp_idx, dutyperiod in enumerate(trip.dutyperiods, start=1):
                    self.debug_write(
                        f"Validating dutyperiod {dp_idx} of {dp_count} for trip "
                        f"{trip.number}",
                        Level.DP,
                    )
                    compact_dutyperiod = dutyperiod_lookup[dutyperiod.compact_uuid]
                    self.validate_dutyperiod(
                        compact_dutyperiod, dutyperiod, ctx, trip.number
                    )
                    flight_lookup = {x.uuid: x for x in compact_dutyperiod.flights}
                    flight_count = len(dutyperiod.flights)
                    for flt_idx, flight in enumerate(dutyperiod.flights, start=1):
                        self.debug_write(
                            f"Validating flight {flight.number}, {flt_idx} of "
                            f"{flight_count}",
                            Level.FLT,
                        )
                        compact_flight = flight_lookup[flight.compact_uuid]
                        self.validate_flight(compact_flight, flight, ctx, trip.number)

    def validate_bid_package(
        self,
        compact_bid: compact.BidPackage,
        expanded_bid: expanded.BidPackage,
        ctx: dict | None,
    ):
        _ = compact_bid
        if not expanded_bid.pages:
            self.debug_write(
                f"Expanded bid package bid has no pages. uuid: {expanded_bid.uuid}",
                Level.PKG + 1,
            )
        trip_count = length(expanded_bid.walk_trips())
        if trip_count < 1:
            self.debug_write(
                f"No trips found in expanded bid package. uuid: {expanded_bid.uuid}",
                Level.PKG + 1,
            )

    def validate_page(
        self,
        compact_page: compact.Page,
        expanded_page: expanded.Page,
        ctx: dict | None,
    ):
        pass
        # trip_lookup = {x.uuid: x for x in compact_page.trips}
        # for trip in expanded_page.trips:
        #     self.validate_trip(trip_lookup[trip.compact_uuid], trip, ctx)

    def validate_trip(
        self,
        compact_trip: compact.Trip,
        expanded_trip: expanded.Trip,
        ctx: dict | None,
    ):
        _ = compact_trip
        self.check_trip_tafb(expanded_trip, ctx)
        self.check_trip_length(expanded_trip, ctx)
        self.check_trip_end(expanded_trip, ctx)

    def check_trip_length(self, expanded_trip: expanded.Trip, ctx: dict | None):
        total = timedelta()
        for dutyperiod in expanded_trip.dutyperiods:
            duration = dutyperiod.release.utc_date - dutyperiod.report.utc_date
            total += duration
            if dutyperiod.layover is not None:
                total += dutyperiod.layover.odl
        if total != expanded_trip.tafb:
            self.debug_write(
                f"Calculated trip length {total} does not match "
                f"parsed trip length {expanded_trip.tafb} for trip {expanded_trip.number} "
                f"uuid: {expanded_trip.uuid} "
                f"compact_uuid: {expanded_trip.compact_uuid} ",
                Level.TRIP + 1,
            )

    def check_trip_tafb(self, expanded_trip: expanded.Trip, ctx: dict | None):
        last_release = expanded_trip.dutyperiods[-1].release.utc_date
        trip_tafb = last_release - expanded_trip.start.utc_date
        if trip_tafb != expanded_trip.tafb:
            self.debug_write(
                f"Calculated trip tafb {trip_tafb} does not match "
                f"parsed trip tafb {expanded_trip.tafb} for trip {expanded_trip.number} "
                f"uuid: {expanded_trip.uuid} "
                f"compact_uuid: {expanded_trip.compact_uuid} ",
                Level.TRIP + 1,
            )

    def check_trip_end(self, expanded_trip: expanded.Trip, ctx: dict | None):
        last_release = expanded_trip.dutyperiods[-1].release
        if last_release != expanded_trip.end:
            self.debug_write(
                f"Computed end of trip {expanded_trip.end!r} does not match last "
                f"dutyperiod release {last_release!r} for trip {expanded_trip.number} "
                f"uuid: {expanded_trip.uuid} "
                f"compact_uuid: {expanded_trip.compact_uuid} ",
                Level.TRIP + 1,
            )

    def validate_dutyperiod(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict | None,
        trip_number: str,
    ):
        self.check_report_times(
            compact_dutyperiod, expanded_dutyperiod, ctx, trip_number
        )
        self.check_release_times(
            compact_dutyperiod, expanded_dutyperiod, ctx, trip_number
        )
        self.check_dutytime(expanded_dutyperiod, ctx, trip_number)

    def check_dutytime(
        self,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict | None,
        trip_number: str,
    ):
        dutytime = (
            expanded_dutyperiod.release.utc_date - expanded_dutyperiod.report.utc_date
        )
        if dutytime != expanded_dutyperiod.duty:
            self.debug_write(
                f"Calculated dutytime {dutytime} does not match "
                f"parsed dutytime {expanded_dutyperiod.duty} "
                f"trip number: {trip_number} "
                f"uuid: {expanded_dutyperiod.uuid} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} "
                f"\n\trelease:{expanded_dutyperiod.release}"
                f"\n\treport:{expanded_dutyperiod.report}",
                Level.DP + 1,
            )

    def check_report_times(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict | None,
        trip_number: str,
    ):
        report_time = expanded_dutyperiod.report.local().time()
        if not compare_time(
            report_time,
            compact_dutyperiod.report.lcl,
            ignore_tz=True,
        ):
            self.debug_write(
                f"Report times do not match. "
                f"compact: {compact_dutyperiod.report}, "
                f"expanded: {expanded_dutyperiod.report}. "
                f"trip number: {trip_number} "
                f"uuid: {expanded_dutyperiod.uuid} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} ",
                Level.DP + 1,
            )

    def check_release_times(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict | None,
        trip_number: str,
    ):
        release_time = expanded_dutyperiod.release.local().time()
        if not compare_time(
            release_time,
            compact_dutyperiod.release.lcl,
            ignore_tz=True,
        ):
            self.debug_write(
                f"Release times do not match. "
                f"compact: {compact_dutyperiod.release.lcl!r}, "
                f"expanded: {release_time!r}. "
                f"trip number: {trip_number} "
                f"uuid: {expanded_dutyperiod.uuid} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} ",
                Level.DP + 1,
            )

    def validate_flight(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        ctx: dict | None,
        trip_number: str,
    ):
        self.check_departure(compact_flight, expanded_flight, ctx, trip_number)
        self.check_arrival(compact_flight, expanded_flight, ctx, trip_number)
        self.check_flight_time(expanded_flight, ctx, trip_number)

    def check_departure(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        ctx: dict | None,
        trip_number: str,
    ):
        departure_time = expanded_flight.departure.local().time()
        if not compare_time(
            departure_time,
            compact_flight.departure.lcl,
            ignore_tz=True,
        ):
            self.debug_write(
                f"Departure times do not match for flight {expanded_flight.number}. "
                f"compact: {compact_flight.departure.lcl!r}, "
                f"expanded: {departure_time!r}. "
                f"trip number: {trip_number} "
                f"uuid: {expanded_flight.uuid} "
                f"compact_uuid: {expanded_flight.compact_uuid} ",
                Level.FLT + 1,
            )

    def check_arrival(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        ctx: dict | None,
        trip_number: str,
    ):
        arrival_time = expanded_flight.arrival.local().time()
        if not compare_time(
            arrival_time,
            compact_flight.arrival.lcl,
            ignore_tz=True,
        ):
            self.debug_write(
                f"Arrival times do not match for flight {expanded_flight.number}. "
                f"compact: {compact_flight.arrival.lcl!r}, "
                f"expanded: {arrival_time!r}. "
                f"trip number: {trip_number} "
                f"uuid: {expanded_flight.uuid} "
                f"compact_uuid: {expanded_flight.compact_uuid} ",
                Level.FLT + 1,
            )

    def check_flight_time(
        self,
        expanded_flight: expanded.Flight,
        ctx: dict | None,
        trip_number: str,
    ):
        flight_time = (
            expanded_flight.arrival.utc_date - expanded_flight.departure.utc_date
        )
        if expanded_flight.deadhead:
            if flight_time != expanded_flight.synth:
                self.debug_write(
                    f"Flight time {flight_time} does not match synth time "
                    f"{expanded_flight.synth} on deadhead flight {expanded_flight.number}. "
                    f"trip number: {trip_number} "
                    f"uuid: {expanded_flight.uuid} "
                    f"compact_uuid: {expanded_flight.compact_uuid} ",
                    Level.FLT + 1,
                )
            return
        if flight_time != expanded_flight.block:
            self.debug_write(
                f"Flight time {flight_time} does not match block time "
                f"{expanded_flight.block} on flight {expanded_flight.number}. "
                f"trip number: {trip_number} "
                f"uuid: {expanded_flight.uuid} "
                f"compact_uuid: {expanded_flight.compact_uuid} "
                f"\n\tdeparture: {expanded_flight.departure_station} {expanded_flight.departure}"
                f"\n\tarrival: {expanded_flight.arrival_station} {expanded_flight.arrival}",
                Level.FLT + 1,
            )

    def validate_layover(
        self,
        compact_layover: compact.Layover,
        expanded_layover: expanded.Layover,
        ctx: dict | None,
    ):
        pass

    def validate_hotel(
        self,
        conpact_hotel: compact.Hotel,
        expanded_hotel: expanded.Hotel,
        ctx: dict | None,
    ):
        pass

    def validate_transportation(
        self,
        compact_transportation: compact.Transportation,
        expanded_transportation: expanded.Transportation,
        ctx: dict | None,
    ):
        pass
