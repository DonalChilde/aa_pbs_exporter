import logging

from aa_pbs_exporter.pbs_2022_01 import messages
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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

    def validate_page(self):
        pass

    def validate_trip(self):
        pass

    def validate_dutyperiod(self):
        pass

    def validate_flight(self):
        pass

    def validate_layover(self):
        pass

    def validate_hotel(self):
        pass

    def validate_transportation(self):
        pass
