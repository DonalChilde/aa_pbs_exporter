import logging
from datetime import datetime, time, timedelta, timezone
from typing import Sequence
from uuid import uuid5
from zoneinfo import ZoneInfo

from aa_pbs_exporter.pbs_2022_01 import validate
from aa_pbs_exporter.pbs_2022_01.helpers.add_timedelta import add_timedelta
from aa_pbs_exporter.pbs_2022_01.helpers.complete_time import complete_time
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.pbs_2022_01.models.common import Instant
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CompactToExpanded:
    def __init__(
        self,
        validator: validate.ExpandedValidator | None,
        msg_bus: Publisher | None,
    ) -> None:
        self.validator = validator
        self.msg_bus = msg_bus

    def send_message(self, msg: MessageProtocol, ctx: dict | None):
        _ = ctx
        logger.info(msg=f"{msg}")
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
        for compact_page in compact_bid_package.pages:
            expanded_bid_package.pages.append(self.translate_page(compact_page))
        if self.validator is not None:
            self.validator.validate_bid_package(
                compact_bid_package, expanded_bid_package, ctx
            )
        return expanded_bid_package

    def translate_page(
        self,
        compact_page: compact.Page,
        ctx: dict | None = None,
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
        )

        for compact_trip in compact_page.trips:
            expanded_page.trips.extend(self.translate_trip(compact_trip))
        if self.validator is not None:
            self.validator.validate_page(compact_page, expanded_page, ctx)
        return expanded_page

    def translate_trip(
        self,
        compact_trip: compact.Trip,
        ctx: dict | None = None,
    ) -> Sequence[expanded.Trip]:
        trips = []
        for start_date in compact_trip.start_dates:
            # NOTE Does not account for times in the fold
            start_utc = datetime.combine(
                start_date,
                compact_trip.dutyperiods[0].report.lcl,
                ZoneInfo(compact_trip.dutyperiods[0].report.tz_name),
            ).astimezone(timezone.utc)
            start = Instant(
                utc_date=start_utc,
                tz_name=compact_trip.dutyperiods[0].report.tz_name,
            )
            end = start + compact_trip.tafb
            expanded_trip = expanded.Trip(
                uuid=uuid5(compact_trip.uuid, start.utc_date.isoformat()),
                compact_uuid=compact_trip.uuid,
                number=compact_trip.number,
                start=start,
                end=end,
                positions=list(compact_trip.positions),
                operations=compact_trip.operations,
                special_qualifications=compact_trip.special_qualifications,
                block=compact_trip.block,
                synth=compact_trip.synth,
                total_pay=compact_trip.total_pay,
                tafb=compact_trip.tafb,
                dutyperiods=[],
            )
            dutyperiod_ref_instant = start + timedelta()
            for compact_dutyperiod in compact_trip.dutyperiods:
                expanded_dutyperiod = self.translate_dutyperiod(
                    report=dutyperiod_ref_instant, compact_dutyperiod=compact_dutyperiod
                )
                if expanded_dutyperiod.layover is not None:
                    dutyperiod_ref_instant = (
                        expanded_dutyperiod.release + expanded_dutyperiod.layover.odl
                    )
                expanded_trip.dutyperiods.append(expanded_dutyperiod)
            trips.append(expanded_trip)
            if self.validator is not None:
                self.validator.validate_trip(compact_trip, expanded_trip, ctx)
        return trips

    def translate_dutyperiod(
        self,
        report: Instant,
        compact_dutyperiod: compact.DutyPeriod,
        ctx: dict | None = None,
    ) -> expanded.DutyPeriod:
        release_utc = report.utc_date + compact_dutyperiod.duty
        release = Instant(
            utc_date=release_utc, tz_name=compact_dutyperiod.release.tz_name
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
            layover=self.translate_layover(compact_dutyperiod.layover),
            flights=[],
        )
        flight_ref_instant = expanded_dutyperiod.report
        for flight in compact_dutyperiod.flights:
            expanded_flight = self.translate_flight(flight_ref_instant, flight)
            expanded_dutyperiod.flights.append(expanded_flight)
            flight_ref_instant = expanded_flight.arrival + expanded_flight.ground
        if self.validator is not None:
            self.validator.validate_dutyperiod(
                compact_dutyperiod, expanded_dutyperiod, ctx
            )
        return expanded_dutyperiod

    def translate_flight(
        self,
        ref_instant: Instant,
        compact_flight: compact.Flight,
        ctx: dict | None = None,
    ) -> expanded.Flight:
        departure_time = compact_flight.departure.lcl.replace(
            tzinfo=ZoneInfo(compact_flight.departure.tz_name)
        )
        departure = complete_time_instant(
            ref_instant=ref_instant,
            new_time=departure_time,
            new_tz_name=compact_flight.departure.tz_name,
        )
        arrival_time = compact_flight.arrival.lcl.replace(
            tzinfo=ZoneInfo(compact_flight.arrival.tz_name)
        )
        arrival = complete_time_instant(
            ref_instant=departure,
            new_time=arrival_time,
            new_tz_name=compact_flight.arrival.tz_name,
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
        if self.validator is not None:
            self.validator.validate_flight(compact_flight, expanded_flight, ctx)
        return expanded_flight

    # def calculate_arrival(
    #     self,
    #     departure: Instant,
    #     compact_flight: compact.Flight,
    # ) -> Instant:
    #     if not compact_flight.deadhead:
    #         arrival_time = departure + compact_flight.block
    #     else:
    #         # NOTE not sure if this is true in all cases
    #         arrival_time = departure + compact_flight.synth
    #     return arrival_time.new_tz(compact_flight.arrival.tz_name)

    def translate_layover(
        self,
        compact_layover: compact.Layover | None,
        ctx: dict | None = None,
    ) -> expanded.Layover | None:
        if compact_layover is None:
            return None
        expanded_layover = expanded.Layover(
            uuid=compact_layover.uuid,
            odl=compact_layover.odl,
            city=compact_layover.city,
            hotel=self.translate_hotel(compact_layover.hotel),
            transportation=self.translate_tranportation(compact_layover.transportation),
            hotel_additional=self.translate_hotel(compact_layover.hotel_additional),
            transportation_additional=self.translate_tranportation(
                compact_layover.transportation_additional
            ),
        )
        if self.validator is not None:
            self.validator.validate_layover(compact_layover, expanded_layover, ctx)
        return expanded_layover

    def translate_hotel(
        self,
        compact_hotel: compact.Hotel | None,
        ctx: dict | None = None,
    ) -> expanded.Hotel | None:
        if compact_hotel is None:
            return None
        expanded_hotel = expanded.Hotel(
            uuid=compact_hotel.uuid, name=compact_hotel.name, phone=compact_hotel.phone
        )
        if self.validator is not None:
            self.validator.validate_hotel(compact_hotel, expanded_hotel, ctx)
        return expanded_hotel

    def translate_tranportation(
        self,
        compact_transportation: compact.Transportation | None,
        ctx: dict | None = None,
    ) -> expanded.Transportation | None:
        if compact_transportation is None:
            return None
        expanded_transportation = expanded.Transportation(
            uuid=compact_transportation.uuid,
            name=compact_transportation.name,
            phone=compact_transportation.phone,
        )
        if self.validator is not None:
            self.validator.validate_transportation(
                compact_transportation, expanded_transportation, ctx
            )
        return expanded_transportation


def compact_to_expanded(compact_package: compact.BidPackage, msg_bus: Publisher):
    validator = validate.ExpandedValidator(msg_bus=msg_bus)
    translator = CompactToExpanded(validator=validator, msg_bus=msg_bus)
    expanded_package = translator.translate(compact_package)
    return expanded_package


def complete_time_instant(
    ref_instant: Instant,
    new_time: time,
    new_tz_name: str,
    is_future: bool = True,
) -> Instant:
    # TODO make snippet

    new_datetime = complete_time(
        ref_datetime=ref_instant.utc_date,
        new_time=new_time,
        is_future=is_future,
    )
    return Instant(utc_date=new_datetime.astimezone(timezone.utc), tz_name=new_tz_name)
