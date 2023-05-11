import logging
from datetime import date
from typing import Iterable, Sequence, Sized, Tuple

from aa_pbs_exporter.pbs_2022_01 import messages
from aa_pbs_exporter.pbs_2022_01.models import compact, raw
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CompactValidator:
    def __init__(self, msg_bus: Publisher | None = None) -> None:
        self.msg_bus = msg_bus

    def send_message(self, msg: MessageProtocol, ctx: dict | None):
        _ = ctx
        logger.warning(msg=f"{msg}")
        print(msg)
        if self.msg_bus is not None:
            self.msg_bus.publish_message(msg=msg)

    def validate_bid_package(
        self, raw_bid: raw.BidPackage, compact_bid: compact.BidPackage, ctx: dict | None
    ):
        self.send_message(
            msg=messages.StatusMessage(
                f"Validating compact bid package. uuid: {compact_bid.uuid}"
            ),
            ctx=ctx,
        )
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
                f"No trips found on compact page. uuid: {compact_page.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_trip(
        self, raw_trip: raw.Trip, compact_trip: compact.Trip, ctx: dict | None
    ):
        if int(raw_trip.header.ops_count) != len(compact_trip.start_dates):
            msg = messages.ValidationMessage(
                f"Ops count for raw trip {int(raw_trip.header.ops_count)} "
                f"does not match start date count {len(compact_trip.start_dates)}. "
                f"uuid: {compact_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        if compact_trip.sum_block() != compact_trip.block:
            msg = messages.ValidationMessage(
                f"Sum of block {compact_trip.sum_block()} does not match parsed block "
                f"{compact_trip.block} for compact trip. uuid: {compact_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        # if compact_trip.sum_synth() != compact_trip.synth:
        #     msg = messages.ValidationMessage(
        #         f"Sum of synth {compact_trip.sum_synth()} does not match parsed synth "
        #         f"{compact_trip.synth} for compact trip. uuid: {compact_trip.uuid}"
        #     )
        #     self.send_message(msg=msg, ctx=ctx)
        sum_total_pay = compact_trip.synth + compact_trip.block
        if sum_total_pay != compact_trip.total_pay:
            msg = messages.ValidationMessage(
                f"Sum of synth {compact_trip.synth} and block {compact_trip.block} "
                f"does not match parsed total pay {compact_trip.total_pay} "
                f"for compact trip. "
                f"uuid: {compact_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        if not compact_trip.positions:
            msg = messages.ValidationMessage(
                f"No positions found for compact trip. uuid: {compact_trip.uuid}"
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
        if compact_dutyperiod.sum_block() != compact_dutyperiod.block:
            msg = messages.ValidationMessage(
                f"Sum of block {compact_dutyperiod.sum_block()} does not match parsed "
                f"block {compact_dutyperiod.block} for compact dutyperiod. "
                f"uuid: {compact_dutyperiod.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        sum_total_pay = compact_dutyperiod.synth + compact_dutyperiod.block
        if sum_total_pay != compact_dutyperiod.total_pay:
            msg = messages.ValidationMessage(
                f"Sum of synth {compact_dutyperiod.synth} and block "
                f"{compact_dutyperiod.block} Does not match parsed "
                f"total {compact_dutyperiod.total_pay} "
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


def length(data: Iterable | Sized) -> int:
    # TODO move to a snippets
    try:
        return len(data)
    except:
        return sum(1 for x in data)
