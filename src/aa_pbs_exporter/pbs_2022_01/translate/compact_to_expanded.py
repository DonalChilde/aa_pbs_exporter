import logging
from datetime import datetime, time, timedelta, timezone
from typing import Sequence
from uuid import uuid5
from zoneinfo import ZoneInfo

from aa_pbs_exporter.pbs_2022_01 import validate
from aa_pbs_exporter.pbs_2022_01.helpers.complete_time import complete_time
from aa_pbs_exporter.pbs_2022_01.helpers.init_publisher import indent_message
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.pbs_2022_01.models.common import Instant
from aa_pbs_exporter.snippets import messages

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
ERROR = "compact.translation.error"
STATUS = "compact.translation.status"
DEBUG = "compact.translation.debug"


class CompactToExpanded:
    def __init__(
        self,
        validator: validate.ExpandedValidator | None,
        msg_bus: messages.MessagePublisher | None,
    ) -> None:
        self.validator = validator
        self.msg_bus = msg_bus

    def send_message(self, msg: messages.Message, ctx: dict | None):
        _ = ctx
        if msg.category == STATUS:
            logger.info("\n\t%s", indent_message(msg))
        elif msg.category == DEBUG:
            logger.debug("\n\t%s", indent_message(msg))
        elif msg.category == ERROR:
            logger.warning("\n\t%s", indent_message(msg))
        if self.msg_bus is not None:
            self.msg_bus.publish_message(msg=msg)

    def translate(
        self,
        compact_bid_package: compact.BidPackage,
        ctx: dict | None = None,
    ) -> expanded.BidPackage:
        expanded_bid_package = expanded.BidPackage(
            uuid=compact_bid_package.uuid, source=compact_bid_package.source, pages=[]
        )
        msg = messages.Message(
            f"Translating data from compact to expanded. {compact_bid_package.source}",
            category=STATUS,
        )
        self.send_message(msg, ctx)
        for page_idx, page in enumerate(compact_bid_package.pages, start=1):
            expanded_page = self.translate_page(page, ctx=ctx)
            expanded_bid_package.pages.append(expanded_page)
            for trip_idx, trip in enumerate(page.trips, start=1):
                expanded_trips = self.translate_trip(trip, ctx=ctx)
                expanded_page.trips.extend(expanded_trips)

        if self.validator is not None:
            self.validator.validate(compact_bid_package, expanded_bid_package, ctx)
        return expanded_bid_package

    def expand_dutyperiods(
        self, compact_trip: compact.Trip, expanded_trip: expanded.Trip, ctx: dict | None
    ) -> Sequence[expanded.DutyPeriod]:
        expanded_dutyperiods: list[expanded.DutyPeriod] = []
        dutyperiod_ref_instant = expanded_trip.start + timedelta()
        dutyperiods_len = len(compact_trip.dutyperiods)
        for idx, compact_dutyperiod in enumerate(compact_trip.dutyperiods, start=1):
            msg = messages.Message(
                f"Expanding Trip:{expanded_trip.number} - "
                f"{expanded_trip.start.local().date()}. dutyperiod {idx} of {dutyperiods_len}",
                category=DEBUG,
            )
            self.send_message(msg=msg, ctx=ctx)
            self.send_message(
                messages.Message(f"report is {dutyperiod_ref_instant}", category=DEBUG),
                ctx=ctx,
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

        # for compact_trip in compact_page.trips:
        #     expanded_page.trips.extend(self.translate_trip(compact_trip, ctx=ctx))
        return expanded_page

    def translate_trip(
        self,
        compact_trip: compact.Trip,
        ctx: dict | None,
    ) -> Sequence[expanded.Trip]:
        msg = messages.Message(
            f"Translating compact trip {compact_trip.number} uuid={compact_trip.uuid}",
            category=DEBUG,
        )
        self.send_message(msg=msg, ctx=ctx)
        trips = []
        for start_date in compact_trip.start_dates:
            # NOTE Does not account for times in the fold
            first_report = compact_trip.dutyperiods[0].report
            start_utc = datetime.combine(
                start_date,
                first_report.lcl,
                ZoneInfo(first_report.tz_name),
            ).astimezone(timezone.utc)
            start = Instant(
                utc_date=start_utc,
                tz_name=first_report.tz_name,
            )
            msg = messages.Message(
                f"Generated start of trip: {start} using {start_date} and {first_report}.",
                category=DEBUG,
            )
            self.send_message(msg=msg, ctx=ctx)
            # Assumes trip starts and ends in same timezone.
            end = start + compact_trip.tafb
            msg = messages.Message(
                f"Calculated trip end time {end} using tafb {compact_trip.tafb}",
                category=DEBUG,
            )
            self.send_message(msg=msg, ctx=ctx)

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
            # dutyperiod_ref_instant = start + timedelta()
            # dutyperiods_len = len(compact_trip.dutyperiods)
            # for idx, compact_dutyperiod in enumerate(compact_trip.dutyperiods, start=1):
            #     logger.debug(
            #         "\n\t\tTrip:%s, dutyperiod %s, report is %s.",
            #         expanded_trip.number,
            #         f"{idx} of {dutyperiods_len}",
            #         dutyperiod_ref_instant,
            #     )
            #     expanded_dutyperiod = self.translate_dutyperiod(
            #         report=dutyperiod_ref_instant,
            #         compact_dutyperiod=compact_dutyperiod,
            #         ctx=ctx,
            #     )
            #     if expanded_dutyperiod.layover is not None:
            #         dutyperiod_ref_instant = (
            #             expanded_dutyperiod.release + expanded_dutyperiod.layover.odl
            #         )
            #     expanded_trip.dutyperiods.append(expanded_dutyperiod)
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
            report, compact_release.lcl, compact_release.tz_name
        )
        msg = messages.Message(
            f"Completed release time {release} using report {report} and compact "
            f"release {compact_release!r}",
            category=DEBUG,
        )
        self.send_message(msg=msg, ctx=ctx)
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
        # flight_ref_instant = expanded_dutyperiod.report
        # flights_len = len(compact_dutyperiod.flights)
        # for idx, flight in enumerate(compact_dutyperiod.flights, start=1):
        #     logger.debug(
        #         "\n\t\t\tFlight %s, ref_instant is %s",
        #         f"{flight.number}, {idx} of {flights_len}",
        #         flight_ref_instant,
        #     )
        #     expanded_flight = self.translate_flight(flight_ref_instant, flight, ctx=ctx)
        #     expanded_dutyperiod.flights.append(expanded_flight)
        #     flight_ref_instant = expanded_flight.arrival + expanded_flight.ground
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
            msg = messages.Message(
                f"Flight {flight.number}, {idx} of {flights_len}, "
                f"ref_instant is {flight_ref_instant} ",
                category=DEBUG,
            )
            self.send_message(msg=msg, ctx=ctx)
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
            naive_time=compact_flight.departure.lcl,
            tz_name=compact_flight.departure.tz_name,
        )
        msg = messages.Message(
            f"Completed {compact_flight.number} departure time {departure} using "
            f"ref_instant {ref_instant} and compact departure {compact_flight.departure}",
            category=DEBUG,
        )
        self.send_message(msg=msg, ctx=ctx)
        arrival = complete_time_instant(
            ref_instant=departure,
            naive_time=compact_flight.arrival.lcl,
            tz_name=compact_flight.arrival.tz_name,
        )
        msg = messages.Message(
            f"Completed {compact_flight.number} arrival time {arrival} using "
            f"departure {departure} and compact arrival {compact_flight.arrival}",
            category=DEBUG,
        )
        self.send_message(msg=msg, ctx=ctx)
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
            if info.hotel is None:
                expanded_hotel = None
            else:
                expanded_hotel = expanded.Hotel(
                    uuid=info.hotel.uuid, name=info.hotel.name, phone=info.hotel.phone
                )
            if info.transportation is None:
                expanded_transportation = None
            else:
                expanded_transportation = expanded.Transportation(
                    uuid=info.transportation.uuid,
                    name=info.transportation.name,
                    phone=info.transportation.phone,
                )
            expanded_hotel_info.append(
                expanded.HotelInfo(
                    hotel=expanded_hotel, transportation=expanded_transportation
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


def compact_to_expanded(
    compact_package: compact.BidPackage, msg_bus: messages.MessagePublisher
):
    validator = validate.ExpandedValidator(msg_bus=msg_bus)
    translator = CompactToExpanded(validator=validator, msg_bus=msg_bus)
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
