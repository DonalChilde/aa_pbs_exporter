import logging
from datetime import date
from typing import Iterable, Sequence, Sized, Tuple

from aa_pbs_exporter.pbs_2022_01 import messages
from aa_pbs_exporter.pbs_2022_01.helpers.length import length
from aa_pbs_exporter.pbs_2022_01.models import compact, raw
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# TODO split individual checks out into functions for clarity
class CompactValidator:
    def __init__(self, msg_bus: Publisher | None = None) -> None:
        self.msg_bus = msg_bus

    def send_message(self, msg: MessageProtocol, ctx: dict | None):
        _ = ctx
        if isinstance(msg, messages.StatusMessage):
            logger.info("%s", msg)
        else:
            logger.warning("%s", msg)
        if self.msg_bus is not None:
            self.msg_bus.publish_message(msg=msg)

    def validate(
        self, raw_bid: raw.BidPackage, compact_bid: compact.BidPackage, ctx: dict | None
    ):
        msg = messages.StatusMessage(
            f"Validating compact bid package. source={compact_bid.source} uuid={compact_bid.uuid}"
        )
        self.send_message(msg, ctx)
        self.validate_bid_package(raw_bid, compact_bid, ctx)
        page_lookup = {x.uuid: x for x in raw_bid.pages}
        page_count = len(compact_bid.pages)
        for page_idx, page in enumerate(compact_bid.pages, start=1):
            logger.debug(
                "Validating page %s", f"{page.number}, {page_idx} of {page_count}"
            )
            raw_page = page_lookup[page.uuid]
            self.validate_page(raw_page, page, ctx)
            trip_lookup = {x.uuid: x for x in raw_page.trips}
            trip_count = len(page.trips)
            for trip_idx, trip in enumerate(page.trips, start=1):
                logger.debug(
                    "Validating trip %s", f"{trip.number}, {trip_idx} of {trip_count}"
                )
                raw_trip = trip_lookup[trip.uuid]
                self.validate_trip(raw_trip, trip, ctx)
                dutyperiod_lookup = {x.uuid: x for x in raw_trip.dutyperiods}
                dp_count = len(trip.dutyperiods)
                for dp_idx, dutyperiod in enumerate(trip.dutyperiods, start=1):
                    logger.debug("Validating dutyperiod %s", f"{dp_idx} of {dp_count}")
                    raw_dutyperiod = dutyperiod_lookup[dutyperiod.uuid]
                    self.validate_dutyperiod(raw_dutyperiod, dutyperiod, ctx)
                    flight_lookup = {
                        x.source.uuid5(): x for x in raw_dutyperiod.flights
                    }
                    flight_count = len(dutyperiod.flights)
                    for flt_idx, flight in enumerate(dutyperiod.flights, start=1):
                        logger.debug(
                            "Validating flight %s",
                            f"{flight.number}, {flt_idx} of {flight_count}",
                        )
                        raw_flight = flight_lookup[flight.uuid]
                        self.validate_flight(raw_flight, flight, ctx)

    def validate_bid_package(
        self, raw_bid: raw.BidPackage, compact_bid: compact.BidPackage, ctx: dict | None
    ):
        if not compact_bid.pages:
            msg = messages.ValidationMessage(
                f"Compact bid has no pages. uuid: {compact_bid.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        compact_trip_count = length(compact_bid.walk_trips())
        raw_trip_count = length(raw_bid.walk_trips())
        if compact_trip_count != raw_trip_count:
            msg = messages.ValidationMessage(
                f"Compact trip count: {compact_trip_count} does not match raw trip "
                f"count: {raw_trip_count}. Check skipped prior month trips. "
                f"uuid: {compact_bid.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        if compact_trip_count < 1:
            msg = messages.ValidationMessage(
                f"No trips found in compact bid package. uuid: {compact_bid.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_page(
        self, raw_page: raw.Page, compact_page: compact.Page, ctx: dict | None
    ):
        if len(compact_page.trips) < 1:
            msg = messages.ValidationMessage(
                f"No trips found on compact page ref={compact_page.number}. Were they all prior month trips? uuid: {compact_page.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_trip(
        self, raw_trip: raw.Trip, compact_trip: compact.Trip, ctx: dict | None
    ):
        ops = int(raw_trip.header.ops_count)
        date_count = len(compact_trip.start_dates)
        if ops != date_count:
            msg = messages.ValidationMessage(
                f"Ops count for raw trip {ops} "
                f"does not match start date count {date_count} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        sum_block = compact_trip.sum_block()
        if sum_block != compact_trip.block:
            msg = messages.ValidationMessage(
                f"Sum of block {sum_block} does not match parsed "
                f"block {compact_trip.block} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)

        sum_total_pay = compact_trip.synth + compact_trip.block
        if sum_total_pay != compact_trip.total_pay:
            msg = messages.ValidationMessage(
                f"Sum of synth and block ({compact_trip.synth} + {compact_trip.block} "
                f"= {sum_total_pay}) "
                f"does not match parsed total pay {compact_trip.total_pay} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        if not compact_trip.positions:
            msg = messages.ValidationMessage(
                f"No positions found "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        for idx, dutyperiod in enumerate(compact_trip.dutyperiods, start=1):
            self.check_indexes(dp_idx=idx, compact_dutyperiod=dutyperiod, ctx=ctx)

    def validate_dutyperiod(
        self,
        raw_dutyperiod: raw.DutyPeriod,
        compact_dutyperiod: compact.DutyPeriod,
        ctx: dict | None,
    ):
        sum_block = compact_dutyperiod.sum_block()
        if sum_block != compact_dutyperiod.block:
            msg = messages.ValidationMessage(
                f"Sum of block {sum_block} does not match parsed "
                f"block {compact_dutyperiod.block} for compact dutyperiod. "
                f"dp_idx={compact_dutyperiod.idx} "
                f"uuid: {compact_dutyperiod.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        sum_total_pay = compact_dutyperiod.synth + compact_dutyperiod.block
        if sum_total_pay != compact_dutyperiod.total_pay:
            msg = messages.ValidationMessage(
                f"Sum of synth and block ({compact_dutyperiod.synth} + "
                f"{compact_dutyperiod.block} = {sum_total_pay}) "
                f"Does not match parsed total {compact_dutyperiod.total_pay} "
                f"dp_idx={compact_dutyperiod.idx} "
                f"uuid: {compact_dutyperiod.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_flight(
        self, raw_flight: raw.Flight, compact_flight: compact.Flight, ctx: dict | None
    ):
        pass

    def validate_layover(
        self,
        raw_laypver: raw.Layover,
        compact_layover: compact.Layover,
        ctx: dict | None,
    ):
        pass

    def validate_hotel(
        self,
        raw_hotel: raw.Hotel | raw.HotelAdditional,
        compact_hotel: compact.Hotel,
        ctx: dict | None,
    ):
        pass

    def validate_transportation(
        self,
        raw_transportation: raw.Transportation | raw.TransportationAdditional,
        compact_transportation: compact.Transportation,
        ctx: dict | None,
    ):
        pass

    def check_calendar_entry_count(
        self, raw_trip: raw.Trip, valid_dates: Sequence[date], ctx: dict | None
    ):
        if not len(raw_trip.calendar_entries) == len(valid_dates):
            msg = messages.ValidationMessage(
                f"Count of calendar_entries: {len(raw_trip.calendar_entries)} does not match valid_dates: {len(valid_dates)}. uuid: {raw_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        return

    def check_start_date(
        self,
        day: Tuple[int, int],
        start_date: date,
        raw_trip: raw.Trip,
        ctx: dict | None,
    ):
        if day[1] != start_date.day:
            msg = messages.ValidationMessage(
                f"Partial date: {day!r} does not match day of date: {start_date.isoformat()}. uuid:{raw_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def check_indexes(
        self, dp_idx, compact_dutyperiod: compact.DutyPeriod, ctx: dict | None
    ):
        if dp_idx != compact_dutyperiod.idx:
            msg = messages.ValidationMessage(
                f"Code idx {dp_idx} does not match parsed dutyperiod index "
                f"{compact_dutyperiod.idx}. uuid:{compact_dutyperiod.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        for flt_idx, flight in enumerate(compact_dutyperiod.flights, start=1):
            if dp_idx != flight.dp_idx:
                msg = messages.ValidationMessage(
                    f"Code idx {flt_idx} does not match parsed dutyperiod idx for "
                    f"flight index {flight.dp_idx}. uuid:{flight.uuid}"
                )
                self.send_message(msg=msg, ctx=ctx)
            if flt_idx != flight.idx:
                msg = messages.ValidationMessage(
                    f"Code idx {flt_idx} does not match parsed flight idx {flight.idx}. "
                    f"uuid:{flight.uuid}"
                )
                self.send_message(msg=msg, ctx=ctx)

    # check against flights.flight too
