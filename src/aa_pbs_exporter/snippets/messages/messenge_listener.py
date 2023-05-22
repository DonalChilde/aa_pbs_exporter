####################################################
#                                                  #
#       src/snippets/messages/messenger.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:26-07:00            #
# Last Modified: 2023-05-22T12:50:58.353940+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from io import TextIOWrapper

from snippets.messages.messenger_protocol import (
    MessageProtocol,
    MessengeListenerProtocol,
)


class MessengeListener(MessengeListenerProtocol):
    def receive_message(self, msg: MessageProtocol):
        raise NotImplementedError

    def format_received_message(self, msg: MessageProtocol) -> str:
        return msg.produce_message()


class PrintMessenger(MessengeListener):
    def __init__(
        self, end: str = "\n", file: TextIOWrapper | None = None, flush: bool = False
    ) -> None:
        super().__init__()
        self.end = end
        self.file = file
        self.flush = flush

    def receive_message(self, msg: MessageProtocol):
        msg_txt = self.format_received_message(msg)
        if msg_txt is not None:
            print(
                msg_txt,
                end=self.end,
                file=self.file,
                flush=self.flush,
            )
