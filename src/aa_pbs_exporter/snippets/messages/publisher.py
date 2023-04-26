####################################################
#                                                  #
#       src/snippets/messages/publisher.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:44-07:00            #
# Last Modified: 2023-04-26T18:16:35.380311+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Sequence

from aa_pbs_exporter.snippets.messages.messenger_protocol import (
    MessageProtocol,
    MessengerProtocol,
    PublisherProtocol,
)


class Publisher(PublisherProtocol):
    def __init__(self, messengers: Sequence[MessengerProtocol]) -> None:
        self.messengers = list(messengers)

    def publish_message(self, msg: MessageProtocol):
        for messenger in self.messengers:
            messenger.send_message(msg=msg)
