####################################################
#                                                  #
#          src/snippets/messages/message.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:14:53-07:00            #
# Last Modified: 2023-05-04T13:50:18.032284+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol


class Message(MessageProtocol):
    def __init__(self, msg: str, extra: dict | None = None) -> None:
        self.msg = msg
        self.extra = extra

    def produce_message(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.msg

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(msg={self.msg}, extra={self.extra!r})"
