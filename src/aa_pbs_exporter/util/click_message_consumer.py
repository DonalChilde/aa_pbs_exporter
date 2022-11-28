####################################################
#                                                  #
#  src/snippets/click/click_message_consumer.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-27T06:42:11-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

from typing import Dict

import click

from .publisher_consumer import MessageConsumer


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
