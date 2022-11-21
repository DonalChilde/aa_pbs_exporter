from typing import Dict
from aa_pbs_exporter.util.publisher_consumer import MessageConsumer
import click


class ClickMessageConsumer(MessageConsumer):
    def consume_message(
        self,
        msg: str,
        *,
        category: str = "",
        level: int | None = None,
        extras: Dict | None = None,
    ):
        click.echo(msg)
