####################################################
#                                                  #
#       src/snippets/messages/messenger.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:26-07:00            #
# Last Modified: 2023-04-26T18:16:35.378182+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from io import TextIOWrapper

from aa_pbs_exporter.snippets.messages.messenger_protocol import (
    MessageProtocol,
    MessengerProtocol,
)


class Messenger(MessengerProtocol):
    def send_message(self, msg: MessageProtocol):
        raise NotImplementedError

    def message_to_txt(self, msg: MessageProtocol):
        return f"{msg}"


class PrintMessenger(Messenger):
    def __init__(
        self, end: str = "\n", file: TextIOWrapper | None = None, flush: bool = False
    ) -> None:
        super().__init__()
        self.end = end
        self.file = file
        self.flush = flush

    def send_message(self, msg: MessageProtocol):
        print(self.message_to_txt(msg), end=self.end, file=self.file, flush=self.flush)
