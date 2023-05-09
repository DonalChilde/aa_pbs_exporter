import logging

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.snippets.messages.message import Message
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RawValidator:
    def __init__(self, msg_bus: Publisher | None = None) -> None:
        self.msg_bus = msg_bus

    def send_message(self, msg: Message, ctx: dict | None):
        _ = ctx
        logger.warning(msg=f"{msg}")
        print(msg)
        if self.msg_bus is not None:
            self.msg_bus.publish_message(msg=msg)

    def validate_bid_package(self, bid_package: raw.BidPackage, ctx: dict | None):
        self.check_bid_for_empty_properies(bid_package=bid_package, ctx=ctx)

    def check_bid_for_empty_properies(
        self, bid_package: raw.BidPackage, ctx: dict | None
    ):
        if not bid_package.pages:
            self.send_message(
                Message(
                    f"Bid package has no pages. uuid: {bid_package.uuid} "
                    f"source: {bid_package.source}"
                ),
                ctx,
            )
        for page in bid_package.pages:
            self.check_page_for_empty_properies(page=page, ctx=ctx)

    def check_page_for_empty_properies(self, page: raw.Page, ctx: dict | None):
        if not page.trips:
            self.send_message(Message(f"Page has no trips. uuid: {page.uuid}"), ctx=ctx)
        if page.page_header_2 is None:
            self.send_message(
                Message(f"Page has no page_header_2. uuid: {page.uuid}"), ctx=ctx
            )
        if page.page_footer is None:
            self.send_message(
                Message(f"Page has no page_footer. uuid: {page.uuid}"), ctx=ctx
            )
        for trip in page.trips:
            self.check_trip_for_empty_properies(trip=trip, ctx=ctx)

    def check_trip_for_empty_properies(self, trip: raw.Trip, ctx: dict | None):
        _ = ctx
        if not trip.dutyperiods:
            self.send_message(
                Message(f"Trip has no dutyperiods. uuid: {trip.uuid}"), ctx=ctx
            )
        if trip.footer is None:
            self.send_message(
                Message(f"Trip has no footer. uuid: {trip.uuid}"), ctx=ctx
            )
        for dutyperiod in trip.dutyperiods:
            self.check_dutyperiod_for_empty_properies(dutyperiod=dutyperiod, ctx=ctx)

    def check_dutyperiod_for_empty_properies(
        self, dutyperiod: raw.DutyPeriod, ctx: dict | None
    ):
        _ = ctx
        if not dutyperiod.flights:
            self.send_message(
                Message(f"Dutyperiod has no flights. uuid: {dutyperiod.uuid}"), ctx=ctx
            )
        if dutyperiod.release is None:
            self.send_message(
                Message(f"Dutyperiod has no release. uuid: {dutyperiod.uuid}"), ctx=ctx
            )
        if dutyperiod.layover is not None:
            self.check_layover_for_empty_properies(layover=dutyperiod.layover, ctx=ctx)

    def check_layover_for_empty_properies(self, layover: raw.Layover, ctx: dict | None):
        _ = ctx
        assert layover is not None
        if layover.hotel is None:
            self.send_message(
                Message(f"Layover has no hotel. uuid: {layover.uuid}"), ctx=ctx
            )
