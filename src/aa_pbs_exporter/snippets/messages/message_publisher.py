####################################################
#                                                  #
#       src/snippets/messages/publisher.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:44-07:00            #
# Last Modified: 2023-05-22T12:50:58.352838+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Sequence

from snippets.messages.messenger_protocol import (
    MessageProtocol,
    MessagePublisherProtocol,
    MessengeListenerProtocol,
)


class MessagePublisher(MessagePublisherProtocol):
    def __init__(self, consumers: Sequence[MessengeListenerProtocol]) -> None:
        self.consumers = list(consumers)

    def publish_message(self, msg: MessageProtocol):
        for consumer in self.consumers:
            consumer.receive_message(msg=msg)
