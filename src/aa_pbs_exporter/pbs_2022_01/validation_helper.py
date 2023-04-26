from aa_pbs_exporter.snippets.messages.message import Message
from aa_pbs_exporter.snippets.messages.publisher import Publisher


def send_validation_message(msg: Message, ctx: dict | None):
    if ctx is None:
        return
    publisher: Publisher | None = ctx.get("validation_publisher", None)
    if publisher is None:
        return
    publisher.publish_message(msg)
