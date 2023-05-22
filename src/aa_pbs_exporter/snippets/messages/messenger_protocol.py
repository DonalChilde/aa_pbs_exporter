####################################################
#                                                  #
#   src/snippets/messages/messenger_protocol.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:08-07:00            #
# Last Modified: 2023-05-04T13:50:18.032783+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Protocol


class MessageProtocol(Protocol):
    def produce_message(self) -> str:
        ...


class MessengerConsumerProtocol(Protocol):
    def consume_message(self, msg: MessageProtocol):
        ...


class MessagePublisherProtocol(Protocol):
    consumers: list[MessengerConsumerProtocol]

    def publish_message(self, msg: MessageProtocol):
        ...
