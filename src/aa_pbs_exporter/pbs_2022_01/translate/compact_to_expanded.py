from io import TextIOWrapper
import logging
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
import traceback
from typing import Self, Sequence
from uuid import uuid5
from zoneinfo import ZoneInfo
from time import perf_counter_ns

from aa_pbs_exporter.pbs_2022_01.helpers import elapsed
from aa_pbs_exporter.pbs_2022_01.helpers.complete_time import complete_time
from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.pbs_2022_01.models.common import Instant
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.string.indent import indent

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
ERROR = "compact.translation.error"
STATUS = "compact.translation.status"
DEBUG = "compact.translation.debug"


class CompactToExpanded:
    def __init__(
        self,
        debug_file: Path | None = None,
    ) -> None:
        self.debug_file = debug_file
        self.debug_fp: TextIOWrapper | None = None

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="a", encoding="utf-8")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug_fp is not None:
            self.debug_fp.close()

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def translate(
        self,
        compact_bid_package: compact.BidPackage,
        ctx: dict | None = None,
    ) -> expanded.BidPackage:
        try:
            return self._translate(compact_bid_package=compact_bid_package, ctx=ctx)
        except Exception as error:
            logger.exception("Unexpected error during translation.")
            self.debug_write("".join(traceback.format_exception(error)), 0)
            raise error

    def _translate(
        self,
        compact_bid_package: compact.BidPackage,
        ctx: dict | None = None,
    ) -> expanded.BidPackage:
        start = perf_counter_ns()
        expanded_bid_package = expanded.BidPackage(
            uuid=compact_bid_package.uuid, source=compact_bid_package.source, pages=[]
        )

        self.debug_write(
            f"********** Translating from compact to expanded. "
            f"uuid:{compact_bid_package.uuid} **********\n",
            Level.PKG,
        )
        for page_idx, page in enumerate(compact_bid_package.pages, start=1):
            self.debug_write(
                f"Translating compact page {page.number} {page_idx} "
                f"of {len(compact_bid_package.pages)} "
                f"uuid: {page.uuid}",
                Level.PAGE,
            )
            expanded_page = self.translate_page(page, ctx=ctx)
            expanded_bid_package.pages.append(expanded_page)
            for trip_idx, trip in enumerate(page.trips, start=1):
                self.debug_write(
                    f"Translating compact trip {trip.number} {trip_idx} "
                    f"of {len(page.trips)} "
                    f"uuid: {trip.uuid}",
                    Level.TRIP,
                )
                expanded_trips = self.translate_trip(trip, ctx=ctx)
                expanded_page.trips.extend(expanded_trips)
        end = perf_counter_ns()
        self.debug_write(
            f"Translation complete in {elapsed.nanos_to_seconds(start,end):4f} seconds."
        )

        return expanded_bid_package

    def expand_dutyperiods(
        self, compact_trip: compact.Trip, expanded_trip: expanded.Trip, ctx: dict | None
    ) -> Sequence[expanded.DutyPeriod]:
        expanded_dutyperiods: list[expanded.DutyPeriod] = []
        dutyperiod_ref_instant = expanded_trip.start + timedelta()
        dutyperiods_len = len(compact_trip.dutyperiods)
        for idx, compact_dutyperiod in enumerate(compact_trip.dutyperiods, start=1):
            self.debug_write(
                f"Translating compact dutyperiod {idx} of {dutyperiods_len} for "
                f"Trip:{expanded_trip.number} - {expanded_trip.start.local().date()}.",
                Level.DP,
            )

            self.debug_write(
                f"report is {dutyperiod_ref_instant}",
                Level.DP + 1,
            )
            expanded_dutyperiod = self.translate_dutyperiod(
                report=dutyperiod_ref_instant,
                compact_dutyperiod=compact_dutyperiod,
                ctx=ctx,
            )
            if expanded_dutyperiod.layover is not None:
                dutyperiod_ref_instant = (
                    expanded_dutyperiod.release + expanded_dutyperiod.layover.odl
                )
                self.debug_write(
                    f"Added layover {expanded_dutyperiod.layover.odl} "
                    f"to release {expanded_dutyperiod.release} to get next report.",
                    Level.DP + 1,
                )
            expanded_dutyperiods.append(expanded_dutyperiod)
        return expanded_dutyperiods

    def translate_page(
        self,
        compact_page: compact.Page,
        ctx: dict | None,
    ) -> expanded.Page:
        expanded_page = expanded.Page(
            uuid=compact_page.uuid,
            base=compact_page.base,
            satellite_base=compact_page.satellite_base,
            equipment=compact_page.equipment,
            division=compact_page.division,
            issued=compact_page.issued,
            effective=compact_page.effective,
            start=compact_page.start,
            end=compact_page.end,
            trips=[],
            number=compact_page.number,
        )
        return expanded_page

    def translate_trip(
        self,
        compact_trip: compact.Trip,
        ctx: dict | None,
    ) -> Sequence[expanded.Trip]:
        trips = []
        for start_date in compact_trip.start_dates:
            # NOTE Does not account for times in the fold
            first_report = compact_trip.dutyperiods[0].report
            start_utc = datetime.combine(
                start_date,
                first_report.lcl.time,
                ZoneInfo(first_report.lcl.tz_name),
            ).astimezone(timezone.utc)
            start = Instant(
                utc_date=start_utc,
                tz_name=first_report.lcl.tz_name,
            )

            self.debug_write(
                f"Generated start of trip: {start} using {start_date} and {first_report}.",
                Level.TRIP + 1,
            )
            # Assumes trip starts and ends in same timezone.
            end = start + compact_trip.tafb

            self.debug_write(
                f"Calculated trip end time {end} using tafb {compact_trip.tafb}",
                Level.TRIP + 1,
            )

            expanded_trip = expanded.Trip(
                uuid=uuid5(compact_trip.uuid, start.utc_date.isoformat()),
                compact_uuid=compact_trip.uuid,
                number=compact_trip.number,
                start=start,
                end=end,
                positions=list(compact_trip.positions),
                operations=compact_trip.operations,
                qualifications=compact_trip.qualifications,
                block=compact_trip.block,
                synth=compact_trip.synth,
                total_pay=compact_trip.total_pay,
                tafb=compact_trip.tafb,
                dutyperiods=[],
            )
            dutyperiods = self.expand_dutyperiods(compact_trip, expanded_trip, ctx=ctx)
            expanded_trip.dutyperiods.extend(dutyperiods)
            trips.append(expanded_trip)
        return trips

    def translate_dutyperiod(
        self,
        report: Instant,
        compact_dutyperiod: compact.DutyPeriod,
        ctx: dict | None,
    ) -> expanded.DutyPeriod:
        compact_release = compact_dutyperiod.release
        release = complete_time_instant(
            report, compact_release.lcl.time, compact_release.lcl.tz_name
        )

        self.debug_write(
            f"Completed release time {release} using report {report} and compact "
            f"release {compact_release!r}",
            Level.DP + 1,
        )
        expanded_dutyperiod = expanded.DutyPeriod(
            uuid=uuid5(compact_dutyperiod.uuid, report.utc_date.isoformat()),
            compact_uuid=compact_dutyperiod.uuid,
            idx=compact_dutyperiod.idx,
            report=report,
            report_station=compact_dutyperiod.report_station,
            release=release,
            release_station=compact_dutyperiod.release_station,
            block=compact_dutyperiod.block,
            synth=compact_dutyperiod.synth,
            total_pay=compact_dutyperiod.total_pay,
            duty=compact_dutyperiod.duty,
            flight_duty=compact_dutyperiod.flight_duty,
            layover=self.translate_layover(compact_dutyperiod.layover, ctx=ctx),
            flights=[],
        )
        expanded_flights = self.expand_flights(
            compact_dutyperiod, expanded_dutyperiod, ctx=ctx
        )
        expanded_dutyperiod.flights.extend(expanded_flights)
        return expanded_dutyperiod

    def expand_flights(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict | None,
    ) -> Sequence[expanded.Flight]:
        flights: list[expanded.Flight] = []
        flight_ref_instant = expanded_dutyperiod.report
        flights_len = len(compact_dutyperiod.flights)
        for idx, flight in enumerate(compact_dutyperiod.flights, start=1):
            self.debug_write(
                f"Translating Flight {flight.number}, {idx} of {flights_len}, "
                f"ref_instant is {flight_ref_instant} ",
                Level.FLT,
            )
            expanded_flight = self.translate_flight(flight_ref_instant, flight, ctx=ctx)
            flights.append(expanded_flight)
            flight_ref_instant = expanded_flight.arrival + expanded_flight.ground
        return flights

    def translate_flight(
        self,
        ref_instant: Instant,
        compact_flight: compact.Flight,
        ctx: dict | None,
    ) -> expanded.Flight:
        _ = ctx
        departure = complete_time_instant(
            ref_instant=ref_instant,
            naive_time=compact_flight.departure.lcl.time,
            tz_name=compact_flight.departure.lcl.tz_name,
        )

        self.debug_write(
            f"Completed {compact_flight.number} departure time {departure} using "
            f"ref_instant {ref_instant} and compact departure {compact_flight.departure}",
            Level.FLT + 1,
        )
        arrival = complete_time_instant(
            ref_instant=departure,
            naive_time=compact_flight.arrival.lcl.time,
            tz_name=compact_flight.arrival.lcl.tz_name,
        )

        self.debug_write(
            f"Completed {compact_flight.number} arrival time {arrival} using "
            f"departure {departure} and compact arrival {compact_flight.arrival}",
            Level.FLT + 1,
        )
        expanded_flight = expanded.Flight(
            uuid=uuid5(compact_flight.uuid, departure.utc_date.isoformat()),
            compact_uuid=compact_flight.uuid,
            dp_idx=compact_flight.dp_idx,
            idx=compact_flight.idx,
            dep_arr_day=compact_flight.dep_arr_day,
            eq_code=compact_flight.eq_code,
            number=compact_flight.number,
            deadhead=compact_flight.deadhead,
            departure_station=compact_flight.departure_station,
            departure=departure,
            meal=compact_flight.meal,
            arrival_station=compact_flight.arrival_station,
            arrival=arrival,
            block=compact_flight.block,
            synth=compact_flight.synth,
            ground=compact_flight.ground,
            equipment_change=compact_flight.equipment_change,
        )
        return expanded_flight

    def translate_layover(
        self,
        compact_layover: compact.Layover | None,
        ctx: dict | None,
    ) -> expanded.Layover | None:
        if compact_layover is None:
            return None
        expanded_layover = expanded.Layover(
            uuid=compact_layover.uuid,
            odl=compact_layover.odl,
            city=compact_layover.city,
            hotel_info=self.translate_hotel_info(compact_layover.hotel_info, ctx=ctx),
        )
        return expanded_layover

    def translate_hotel_info(
        self, compact_hotel_info: Sequence[compact.HotelInfo], ctx: dict | None
    ):
        _ = ctx
        expanded_hotel_info: list[expanded.HotelInfo] = []
        for info in compact_hotel_info:
            # if info.hotel is None:
            #     expanded_hotel = None
            # else:
            expanded_hotel = expanded.Hotel(
                uuid=info.hotel.uuid, name=info.hotel.name, phone=info.hotel.phone
            )
            expanded_transportations = []
            for compact_trans in info.transportation:
                expanded_transportation = expanded.Transportation(
                    uuid=compact_trans.uuid,
                    name=compact_trans.name,
                    phone=compact_trans.phone,
                )
                expanded_transportations.append(expanded_transportation)
            expanded_hotel_info.append(
                expanded.HotelInfo(
                    hotel=expanded_hotel, transportation=expanded_transportations
                )
            )
        return expanded_hotel_info

    def translate_hotel(
        self,
        compact_hotel: compact.Hotel | None,
        ctx: dict | None,
    ) -> expanded.Hotel | None:
        _ = ctx
        if compact_hotel is None:
            return None
        expanded_hotel = expanded.Hotel(
            uuid=compact_hotel.uuid, name=compact_hotel.name, phone=compact_hotel.phone
        )
        return expanded_hotel

    def translate_tranportation(
        self,
        compact_transportation: compact.Transportation | None,
        ctx: dict | None = None,
    ) -> expanded.Transportation | None:
        _ = ctx
        if compact_transportation is None:
            return None
        expanded_transportation = expanded.Transportation(
            uuid=compact_transportation.uuid,
            name=compact_transportation.name,
            phone=compact_transportation.phone,
        )
        return expanded_transportation


def translate_compact_to_expanded(
    compact_package: compact.BidPackage,
    debug_file: Path | None = None,
):
    with CompactToExpanded(debug_file=debug_file) as translator:
        expanded_package = translator.translate(compact_package)
    return expanded_package


def complete_time_instant(
    ref_instant: Instant,
    naive_time: time,
    tz_name: str,
    is_future: bool = True,
) -> Instant:
    # TODO make snippet
    # NOTE uses tz_name to replace tzinfo on new time

    new_datetime = complete_time(
        ref_datetime=ref_instant.utc_date,
        new_time=naive_time.replace(tzinfo=ZoneInfo(tz_name)),
        is_future=is_future,
    )
    instant = Instant(utc_date=new_datetime.astimezone(timezone.utc), tz_name=tz_name)
    if instant.local().time().hour != naive_time.hour:
        raise ValueError("WTF!")
    return instant
