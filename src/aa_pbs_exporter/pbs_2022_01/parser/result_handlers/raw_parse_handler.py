# type: ignore

import logging
from datetime import UTC, datetime
from io import TextIOWrapper
from time import perf_counter_ns
from typing import Generic, TypeVar

from aa_pbs_exporter.pbs_2022_01 import translate
from aa_pbs_exporter.pbs_2022_01.helpers import elapsed
from aa_pbs_exporter.snippets import messages
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseResultProtocol,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ERROR = "parse.error"
STATUS = "parse.status"
DEBUG = "parse.debug"

T = TypeVar("T")


class RawResultHandler(Generic[T]):
    def __init__(
        self,
        translator: translate.ParsedToRaw,
        debug_fp: TextIOWrapper | None = None,
        msg_bus: messages.MessagePublisher | None = None,
    ) -> None:
        super().__init__()
        self.translator = translator
        self.msg_bus = msg_bus
        self._debug_fp = debug_fp
        self.data: T | None = None
        self.start: int = 0
        self.end: int = 0

    @property
    def debug_fp(self) -> TextIOWrapper | None:
        return self._debug_fp

    @debug_fp.setter
    def debug_fp(self, value: TextIOWrapper | None):
        self._debug_fp = value
        self.translator.debug_fp = value
        if self.translator.validator is not None:
            self.translator.validator.debug_fp = value

    # def send_message(self, msg: messages.Message, ctx: dict | None):
    #     _ = ctx
    #     if msg.category == STATUS:
    #         logger.info("\n\t%s", indent_message(msg))
    #     elif msg.category == DEBUG:
    #         logger.debug("\n\t%s", indent_message(msg))
    #     elif msg.category == ERROR:
    #         logger.warning("\n\t%s", indent_message(msg))
    #     if self.debug_fp is not None:
    #         self.debug_fp.write(msg.produce_message())
    #     if self.msg_bus is not None:
    #         self.msg_bus.publish_message(msg=msg)

    def debug_write(self, value: str):
        if self.debug_fp is not None:
            print(value, file=self.debug_fp)

    def initialize(self, ctx: dict | None = None):
        _ = ctx
        # msg = messages.Message(msg="Parse result handler initialized.", category=DEBUG)
        # self.send_message(msg=msg, ctx=ctx)
        self.debug_write(
            f"********** Parse started on {datetime.now(UTC).isoformat()} **********\n"
        )
        self.start = perf_counter_ns()

    def handle_result(
        self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
    ):
        _ = kwargs, ctx

        # msg = messages.Message(f"{parse_result}", category=DEBUG)
        # self.send_message(msg=msg, ctx=ctx)
        self.debug_write(str(parse_result))
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
            case "PriorMonthDeadhead":
                self.translator.prior_month_deadhead(data)
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
        self.debug_write("\n********** Finalize Translation **********\n")
        self.translator.parse_complete(ctx=ctx)
        self.data = self.translator.bid_package
        self.end = perf_counter_ns()
        self.debug_write(
            f"********** Parse complete in {elapsed.nanos_to_seconds(self.start,self.end):4f} seconds. **********\n"
        )

    def result_data(self) -> T | None:
        return self.data
