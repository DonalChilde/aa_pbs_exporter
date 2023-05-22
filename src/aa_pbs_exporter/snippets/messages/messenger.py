####################################################
#                                                  #
#       src/snippets/messages/messenger.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:26-07:00            #
# Last Modified: 2023-05-08T23:53:09.225267+00:00  #
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
        msg_txt = self._format_message(msg)
        if msg_txt is not None:
            print(
                msg_txt,
                end=self.end,
                file=self.file,
                flush=self.flush,
            )

    def _format_message(self, msg: MessageProtocol) -> str | None:
        return msg.produce_message()
