####################################################
#                                                  #
#   src/snippets/messages/messenger_protocol.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:08-07:00            #
# Last Modified: 2023-04-26T18:16:35.379622+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Protocol


class MessageProtocol(Protocol):
    msg: str
    extra: dict | None


class MessengerProtocol(Protocol):
    def send_message(self, msg: MessageProtocol):
        ...

    def message_to_txt(self, msg: MessageProtocol):
        ...


class PublisherProtocol(Protocol):
    messengers: list[MessengerProtocol]

    def publish_message(self, msg: MessageProtocol):
        ...
        # for messenger in self.messengers:
        #     messenger.send_message(msg=msg)
