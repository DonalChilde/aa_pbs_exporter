####################################################
#                                                  #
#       src/snippets/messages/publisher.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:44-07:00            #
# Last Modified: 2023-05-22T17:42:40.603070+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Sequence

from .message import Message
from .messenge_listener import MessengeListener


class MessagePublisher:
    def __init__(self, listeners: Sequence[MessengeListener]) -> None:
        self.listeners = list(listeners)

    def publish_message(self, msg: Message):
        for listener in self.listeners:
            listener.receive_message(msg=msg)
