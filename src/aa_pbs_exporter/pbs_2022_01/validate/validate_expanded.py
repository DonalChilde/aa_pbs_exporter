import logging

from aa_pbs_exporter.pbs_2022_01 import messages
from aa_pbs_exporter.pbs_2022_01.helpers.compare_time import compare_time
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

TIME = "%H%M"


class ExpandedValidator:
    def __init__(self, msg_bus: Publisher | None = None) -> None:
        self.msg_bus = msg_bus

    def send_message(self, msg: MessageProtocol, ctx: dict | None):
        _ = ctx
        logger.warning(msg=f"{msg}")
        if self.msg_bus is not None:
            self.msg_bus.publish_message(msg=msg)

    def validate_bid_package(
        self,
        compact_bid: compact.BidPackage,
        expanded_bid: expanded.BidPackage,
        ctx: dict | None,
    ):
        self.send_message(
            msg=messages.StatusMessage(
                f"Validating expanded bid package. uuid: {expanded_bid.uuid}"
            ),
            ctx=ctx,
        )

    def validate_page(
        self,
        compact_page: compact.Page,
        expanded_page: expanded.Page,
        ctx: dict | None,
    ):
        pass

    def validate_trip(
        self,
        compact_trip: compact.Trip,
        expanded_trip: expanded.Trip,
        ctx: dict | None,
    ):
        trip_length = expanded_trip.end.utc_date - expanded_trip.start.utc_date
        if trip_length != compact_trip.tafb:
            msg = messages.ValidationMessage(
                msg=f"Calculated trip length {trip_length} does not match parsed trip length {compact_trip.tafb}. uuid: {expanded_trip.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_dutyperiod(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict | None,
    ):
        c_report = compact_dutyperiod.report.lcl.strftime(TIME)
        e_report = expanded_dutyperiod.report.local().strftime(TIME)
        if c_report != e_report:
            msg = messages.ValidationMessage(
                msg=f"Report times do not match. compact: {c_report}, expanded: {e_report}. uuid: {expanded_dutyperiod.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        c_release = compact_dutyperiod.release.lcl.strftime(TIME)
        e_release = expanded_dutyperiod.release.local().strftime(TIME)
        if c_release != e_release:
            msg = messages.ValidationMessage(
                msg=f"Release times do not match. compact: {c_release}, expanded: {e_release}. uuid: {expanded_dutyperiod.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)
        dutytime = (
            expanded_dutyperiod.release.utc_date - expanded_dutyperiod.report.utc_date
        )
        if dutytime != expanded_dutyperiod.duty:
            msg = messages.ValidationMessage(
                msg=f"Calculated dutytime {dutytime} does not match parsed dutytime {expanded_dutyperiod.duty} uuid: {expanded_dutyperiod.uuid}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_flight(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        ctx: dict | None = None,
    ):
        compare_time(
            expanded_flight.arrival.local().time(),
            compact_flight.arrival.lcl,
            ignore_tz=True,
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
