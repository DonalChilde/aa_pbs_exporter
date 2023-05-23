# type: ignore

import logging

from aa_pbs_exporter.pbs_2022_01 import translate
from aa_pbs_exporter.pbs_2022_01.helpers.init_publisher import indent_message
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.snippets import messages
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseResultProtocol,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ERROR = "parse.error"
STATUS = "parse.status"
DEBUG = "parse.debug"


class RawResultHandler:
    def __init__(
        self,
        translator: translate.ParsedToRaw,
        msg_bus: messages.MessagePublisher | None = None,
    ) -> None:
        super().__init__()
        self.translator = translator
        self.msg_bus = msg_bus
        self.data: raw.BidPackage | None = None

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

    def initialize(self, ctx: dict | None = None):
        _ = ctx
        msg = messages.Message(msg="Parse result handler initialized.", category=STATUS)
        self.send_message(msg=msg, ctx=ctx)

    def handle_result(
        self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
    ):
        _ = kwargs, ctx

        msg = messages.Message(f"{parse_result}", category=DEBUG)
        self.send_message(msg=msg, ctx=ctx)
        data = parse_result.parsed_data
        match_value = data.__class__.__qualname__
        match match_value:
            case "PageHeader1":
                self.translator.page_header1(data)
            case "PageHeader2":
                self.translator.page_header2(data)
            case "HeaderSeparator":
                self.translator.header_separator(data)
            case "BaseEquipment":
                self.translator.base_equipment(data)
            case "TripHeader":
                self.translator.trip_header(data)
            case "DutyPeriodReport":
                self.translator.duty_period_report(data)
            case "Flight":
                self.translator.flight(data)
            case "DutyPeriodRelease":
                self.translator.duty_period_release(data)
            case "Hotel":
                self.translator.hotel(data)
            case "HotelAdditional":
                self.translator.hotel_additional(data)
            case "Transportation":
                self.translator.transportation(data)
            case "TransportationAdditional":
                self.translator.transportation_additional(data)
            case "CalendarOnly":
                self.translator.calendar_only(data)
            case "TripFooter":
                self.translator.trip_footer(data)
            case "TripSeparator":
                self.translator.trip_separator(data)
            case "PageFooter":
                self.translator.page_footer(data)

    def finalize(self, ctx: dict | None = None):
        self.translator.parse_complete(ctx=ctx)
        self.data = self.translator.bid_package
        msg = messages.Message(msg="Parse result handler finalized.", category=STATUS)
        self.send_message(msg=msg, ctx=ctx)

    def result_data(self) -> raw.BidPackage | None:
        return self.data
