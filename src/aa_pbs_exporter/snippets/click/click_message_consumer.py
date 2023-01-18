####################################################
#                                                  #
#  src/snippets/click/click_message_consumer.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-27T06:42:11-07:00            #
# Last Modified: 2022-12-04T00:33:38.355611+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

from typing import Dict

import click

from aa_pbs_exporter.snippets.messages.publisher_consumer import MessageConsumerProtocol


class ClickMessageConsumer(MessageConsumerProtocol):
    def consume_message(
        self,
        msg: str,
        *,
        category: str = "",
        level: int | None = None,
        extras: Dict | None = None,
    ):
        click.echo(msg)
