import logging

from aa_pbs_exporter.snippets.messages.message import Message
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ExpandedValidator:
    def __init__(self, publisher: Publisher | None) -> None:
        self.publisher = publisher

    def send_message(self, msg: Message, ctx: dict | None):
        logger.warning(msg=f"{msg}")
        print(msg)
        if self.publisher is not None:
            self.publisher.publish_message(msg=msg)

    def validate_bid_package(self):
        pass

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
