import logging

from aa_pbs_exporter.pbs_2022_01.helpers.init_publisher import indent_message
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.snippets import messages

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ERROR = "raw.validation.error"
STATUS = "raw.validation.status"
DEBUG = "raw.validation.debug"


class RawValidator:
    def __init__(self, msg_bus: messages.MessagePublisher | None = None) -> None:
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

    def validate(self, bid_package: raw.BidPackage, ctx: dict | None):
        msg = messages.Message(
            f"Validating raw bid package. source={bid_package.source} "
            f"uuid={bid_package.uuid}",
            category=STATUS,
        )
        self.send_message(msg, ctx)
        self.validate_bid_package(bid_package, ctx)
        page_count = len(bid_package.pages)
        for page_idx, page in enumerate(bid_package.pages, start=1):
            msg = messages.Message(
                f"Validating page {page_idx} of {page_count}",
                category=STATUS,
            )
            self.send_message(msg, ctx)
            trip_count = len(page.trips)
            self.validate_page(page, ctx)
            for trip_idx, trip in enumerate(page.trips, start=1):
                msg = messages.Message(
                    f"Validating trip {trip.header.number}, {trip_idx} of {trip_count}",
                    category=STATUS,
                )
                self.send_message(msg, ctx)
                self.validate_trip(trip, ctx)
                dp_count = len(trip.dutyperiods)
                for dp_idx, dutyperiod in enumerate(trip.dutyperiods, start=1):
                    msg = messages.Message(
                        f"Validating dutyperiod {dp_idx} of {dp_count}",
                        category=STATUS,
                    )
                    self.send_message(msg, ctx)
                    self.validate_dutyperiod(dutyperiod, ctx)
                    flight_count = len(dutyperiod.flights)
                    for flt_idx, flight in enumerate(dutyperiod.flights, start=1):
                        msg = messages.Message(
                            f"Validating flight {flight.flight_number}, {flt_idx} of {flight_count}",
                            category=STATUS,
                        )
                        self.send_message(msg, ctx)
                        self.validate_flight(flight, ctx)

    def validate_bid_package(self, bid_package: raw.BidPackage, ctx: dict | None):
        self.check_bid_for_empty_properies(bid_package=bid_package, ctx=ctx)

    def validate_page(self, page: raw.Page, ctx: dict | None):
        self.check_page_for_empty_properies(page=page, ctx=ctx)

    def validate_trip(self, trip: raw.Trip, ctx: dict | None):
        self.check_trip_for_empty_properies(trip=trip, ctx=ctx)

    def validate_dutyperiod(self, dutyperiod: raw.DutyPeriod, ctx: dict | None):
        self.check_dutyperiod_for_empty_properies(dutyperiod=dutyperiod, ctx=ctx)

    def validate_layover(self, layover: raw.Layover, ctx: dict | None):
        self.check_layover_for_empty_properies(layover, ctx)

    def validate_flight(self, flight: raw.Flight, ctx: dict | None):
        pass

    def check_bid_for_empty_properies(
        self, bid_package: raw.BidPackage, ctx: dict | None
    ):
        if not bid_package.pages:
            self.send_message(
                messages.Message(
                    f"Bid package has no pages. uuid: {bid_package.uuid} "
                    f"source: {bid_package.source}",
                    category=ERROR,
                ),
                ctx,
            )

    def check_page_for_empty_properies(self, page: raw.Page, ctx: dict | None):
        if not page.trips:
            self.send_message(
                messages.Message(
                    f"Page has no trips. uuid: {page.uuid}",
                    category=ERROR,
                ),
                ctx=ctx,
            )
        if page.page_header_2 is None:
            self.send_message(
                messages.Message(
                    f"Page has no page_header_2. uuid: {page.uuid}",
                    category=ERROR,
                ),
                ctx=ctx,
            )
        if page.page_footer is None:
            self.send_message(
                messages.Message(
                    f"Page has no page_footer. uuid: {page.uuid}",
                    category=ERROR,
                ),
                ctx=ctx,
            )

    def check_trip_for_empty_properies(self, trip: raw.Trip, ctx: dict | None):
        _ = ctx
        if not trip.dutyperiods:
            self.send_message(
                messages.Message(
                    f"Trip has no dutyperiods. uuid: {trip.uuid}",
                    category=ERROR,
                ),
                ctx=ctx,
            )
        if trip.footer is None:
            self.send_message(
                messages.Message(
                    f"Trip has no footer. uuid: {trip.uuid}",
                    category=ERROR,
                ),
                ctx=ctx,
            )

    def check_dutyperiod_for_empty_properies(
        self, dutyperiod: raw.DutyPeriod, ctx: dict | None
    ):
        _ = ctx
        if not dutyperiod.flights:
            self.send_message(
                messages.Message(
                    f"Dutyperiod has no flights. uuid: {dutyperiod.uuid}",
                    category=ERROR,
                ),
                ctx=ctx,
            )
        if dutyperiod.release is None:
            self.send_message(
                messages.Message(
                    f"Dutyperiod has no release. uuid: {dutyperiod.uuid}",
                    category=ERROR,
                ),
                ctx=ctx,
            )
        if dutyperiod.layover is not None:
            self.check_layover_for_empty_properies(layover=dutyperiod.layover, ctx=ctx)

    def check_layover_for_empty_properies(self, layover: raw.Layover, ctx: dict | None):
        _ = ctx
        assert layover is not None
        if layover.hotel_info[0].hotel is None:
            self.send_message(
                messages.Message(
                    f"Layover has no primary hotel. uuid: {layover.uuid}",
                    category=ERROR,
                ),
                ctx=ctx,
            )
