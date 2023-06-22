from io import TextIOWrapper
import logging

from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
from aa_pbs_exporter.pbs_2022_01.helpers.init_publisher import indent_message
from aa_pbs_exporter.pbs_2022_01.helpers.length import length
from aa_pbs_exporter.pbs_2022_01.models import compact, raw
from aa_pbs_exporter.snippets import messages

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ERROR = "compact.validation.error"
STATUS = "compact.validation.status"
DEBUG = "compact.validation.debug"


# TODO split individual checks out into functions for clarity
class CompactValidator:
    def __init__(
        self,
        msg_bus: messages.MessagePublisher | None = None,
        debug_fp: TextIOWrapper | None = None,
    ) -> None:
        self.msg_bus = msg_bus
        self.debug_fp = debug_fp

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

    def validate(
        self, raw_bid: raw.BidPackage, compact_bid: compact.BidPackage, ctx: dict | None
    ):
        msg = messages.Message(
            f"Validating compact bid package. uuid={compact_bid.uuid}",
            category=STATUS,
            level=Level.PKG,
        )
        self.send_message(msg, ctx)
        self.validate_bid_package(raw_bid, compact_bid, ctx)
        page_lookup = {x.uuid: x for x in raw_bid.pages}
        page_count = len(compact_bid.pages)
        for page_idx, page in enumerate(compact_bid.pages, start=1):
            msg = messages.Message(
                f"Validating page {page.number}, {page_idx} of {page_count}",
                category=DEBUG,
                level=Level.PAGE,
            )
            self.send_message(msg=msg, ctx=ctx)
            raw_page = page_lookup[page.uuid]
            self.validate_page(raw_page, page, ctx)
            trip_lookup = {x.uuid: x for x in raw_page.trips}
            trip_count = len(page.trips)
            for trip_idx, trip in enumerate(page.trips, start=1):
                msg = messages.Message(
                    f"Validating trip {trip.number}, {trip_idx} of {trip_count}",
                    category=DEBUG,
                    level=Level.TRIP,
                )
                self.send_message(msg=msg, ctx=ctx)

                raw_trip = trip_lookup[trip.uuid]
                self.validate_trip(raw_trip, trip, ctx)
                dutyperiod_lookup = {x.uuid: x for x in raw_trip.dutyperiods}
                dp_count = len(trip.dutyperiods)
                for dp_idx, dutyperiod in enumerate(trip.dutyperiods, start=1):
                    msg = messages.Message(
                        f"Validating dutyperiod {dp_idx} of {dp_count}",
                        category=DEBUG,
                        level=Level.DP,
                    )
                    self.send_message(msg=msg, ctx=ctx)
                    raw_dutyperiod = dutyperiod_lookup[dutyperiod.uuid]
                    self.validate_dutyperiod(raw_dutyperiod, dutyperiod, ctx)
                    flight_lookup = {
                        x.source.uuid5(): x for x in raw_dutyperiod.flights
                    }
                    flight_count = len(dutyperiod.flights)
                    for flt_idx, flight in enumerate(dutyperiod.flights, start=1):
                        msg = messages.Message(
                            f"Validating flight {flight.number}, {flt_idx} of {flight_count}",
                            category=DEBUG,
                            level=Level.FLT,
                        )
                        self.send_message(msg=msg, ctx=ctx)
                        raw_flight = flight_lookup[flight.uuid]
                        self.validate_flight(raw_flight, flight, ctx)

    def validate_bid_package(
        self, raw_bid: raw.BidPackage, compact_bid: compact.BidPackage, ctx: dict | None
    ):
        if not compact_bid.pages:
            msg = messages.Message(
                f"Compact bid has no pages. uuid: {compact_bid.uuid}",
                category=ERROR,
                level=Level.PKG + 1,
            )
            self.send_message(msg=msg, ctx=ctx)
        compact_trip_count = length(compact_bid.walk_trips())
        raw_trip_count = length(raw_bid.walk_trips())
        if compact_trip_count != raw_trip_count:
            msg = messages.Message(
                f"Compact trip count: {compact_trip_count} does not match raw trip "
                f"count: {raw_trip_count}. Check skipped prior month trips. "
                f"uuid: {compact_bid.uuid}",
                category=ERROR,
                level=Level.PKG + 1,
            )
            self.send_message(msg=msg, ctx=ctx)
        if compact_trip_count < 1:
            msg = messages.Message(
                f"No trips found in compact bid package. uuid: {compact_bid.uuid}",
                category=ERROR,
                level=Level.PKG + 1,
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_page(
        self, raw_page: raw.Page, compact_page: compact.Page, ctx: dict | None
    ):
        if len(compact_page.trips) < 1:
            msg = messages.Message(
                f"No trips found on compact page ref={compact_page.number}. "
                f"Were they all prior month trips? uuid: {compact_page.uuid}",
                category=ERROR,
                level=Level.PAGE + 1,
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_trip(
        self, raw_trip: raw.Trip, compact_trip: compact.Trip, ctx: dict | None
    ):
        ops = int(raw_trip.header.ops_count)
        date_count = len(compact_trip.start_dates)
        if ops != date_count:
            msg = messages.Message(
                f"Ops count for raw trip {ops} "
                f"does not match start date count {date_count} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}",
                category=ERROR,
                level=Level.TRIP + 1,
            )
            self.send_message(msg=msg, ctx=ctx)
        sum_block = compact_trip.sum_block()
        if sum_block != compact_trip.block:
            msg = messages.Message(
                f"Sum of block {sum_block} does not match parsed "
                f"block {compact_trip.block} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}",
                category=ERROR,
                level=Level.TRIP + 1,
            )
            self.send_message(msg=msg, ctx=ctx)

        sum_total_pay = compact_trip.synth + compact_trip.block
        if sum_total_pay != compact_trip.total_pay:
            msg = messages.Message(
                f"Sum of synth and block ({compact_trip.synth} + {compact_trip.block} "
                f"= {sum_total_pay}) "
                f"does not match parsed total pay {compact_trip.total_pay} "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}",
                category=ERROR,
                level=Level.TRIP + 1,
            )
            self.send_message(msg=msg, ctx=ctx)
        if not compact_trip.positions:
            msg = messages.Message(
                f"No positions found "
                f"for compact trip {compact_trip.number}. "
                f"uuid: {compact_trip.uuid}",
                category=ERROR,
                level=Level.TRIP + 1,
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
            msg = messages.Message(
                f"Sum of block {sum_block} does not match parsed "
                f"block {compact_dutyperiod.block} for compact dutyperiod. "
                f"dp_idx={compact_dutyperiod.idx} "
                f"uuid: {compact_dutyperiod.uuid}",
                category=ERROR,
                level=Level.DP + 1,
            )
            self.send_message(msg=msg, ctx=ctx)
        sum_total_pay = compact_dutyperiod.synth + compact_dutyperiod.block
        if sum_total_pay != compact_dutyperiod.total_pay:
            msg = messages.Message(
                f"Sum of synth and block ({compact_dutyperiod.synth} + "
                f"{compact_dutyperiod.block} = {sum_total_pay}) "
                f"Does not match parsed total {compact_dutyperiod.total_pay} "
                f"dp_idx={compact_dutyperiod.idx} "
                f"uuid: {compact_dutyperiod.uuid}",
                category=ERROR,
                level=Level.DP + 1,
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

    def check_indexes(
        self, dp_idx, compact_dutyperiod: compact.DutyPeriod, ctx: dict | None
    ):
        # TODO refactor into separate functions
        if dp_idx != compact_dutyperiod.idx:
            msg = messages.Message(
                f"Code idx {dp_idx} does not match parsed dutyperiod index "
                f"{compact_dutyperiod.idx}. "
                f"uuid:{compact_dutyperiod.uuid}",
                category=ERROR,
                level=Level.DP + 1,
            )
            self.send_message(msg=msg, ctx=ctx)
        for flt_idx, flight in enumerate(compact_dutyperiod.flights, start=1):
            if dp_idx != flight.dp_idx:
                msg = messages.Message(
                    f"Code idx {flt_idx} does not match parsed dutyperiod idx for "
                    f"flight index {flight.dp_idx}. "
                    f"uuid:{flight.uuid}",
                    category=ERROR,
                    level=Level.FLT + 1,
                )
                self.send_message(msg=msg, ctx=ctx)
            if flt_idx != flight.idx:
                msg = messages.Message(
                    f"Code idx {flt_idx} does not match parsed flight idx {flight.idx}. "
                    f"uuid:{flight.uuid}",
                    category=ERROR,
                    level=Level.FLT + 1,
                )
                self.send_message(msg=msg, ctx=ctx)
