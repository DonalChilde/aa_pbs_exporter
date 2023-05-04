####################################################
#                                                  #
#       src/snippets/messages/publisher.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:44-07:00            #
# Last Modified: 2023-05-04T13:50:18.033276+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Sequence

from aa_pbs_exporter.snippets.messages.messenger_protocol import (
    MessageProtocol,
    MessagePublisherProtocol,
    MessengerConsumerProtocol,
)


class Publisher(MessagePublisherProtocol):
    def __init__(self, consumers: Sequence[MessengerConsumerProtocol]) -> None:
        self.consumers = list(consumers)

    def publish_message(self, msg: MessageProtocol):
        for consumer in self.consumers:
            consumer.consume_message(msg=msg)
