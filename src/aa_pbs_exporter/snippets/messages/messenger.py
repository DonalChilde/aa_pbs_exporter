####################################################
#                                                  #
#       src/snippets/messages/messenger.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:26-07:00            #
# Last Modified: 2023-05-04T13:50:18.031673+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from io import TextIOWrapper

from aa_pbs_exporter.snippets.messages.messenger_protocol import (
    MessageProtocol,
    MessengerConsumerProtocol,
)


class Messenger(MessengerConsumerProtocol):
    def consume_message(self, msg: MessageProtocol):
        raise NotImplementedError


class PrintMessenger(Messenger):
    def __init__(
        self, end: str = "\n", file: TextIOWrapper | None = None, flush: bool = False
    ) -> None:
        super().__init__()
        self.end = end
        self.file = file
        self.flush = flush

    def consume_message(self, msg: MessageProtocol):
        print(
            self._format_message(msg=msg),
            end=self.end,
            file=self.file,
            flush=self.flush,
        )

    def _format_message(self, msg: MessageProtocol) -> str:
        return msg.produce_message()
