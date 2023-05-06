import logging

from aa_pbs_exporter.snippets.messages.message import Message
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def send_validation_message(msg: Message, ctx: dict | None):
    logger.warning(msg=f"{msg}")
    if ctx is None:
        return
    publisher: Publisher | None = ctx.get("validation_publisher", None)
    if publisher is None:
        return
    publisher.publish_message(msg)
