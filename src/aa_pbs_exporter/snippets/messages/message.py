####################################################
#                                                  #
#          src/snippets/messages/message.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:14:53-07:00            #
# Last Modified: 2023-05-22T12:50:58.353417+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from snippets.messages.messenger_protocol import MessageProtocol


class Message(MessageProtocol):
    def __init__(
        self,
        msg: str,
        *,
        category: str = "",
        level: int | None = None,
        extra: dict | None = None,
    ) -> None:
        self.msg = msg
        self.extra = extra
        self.category = category
        self.level = level

    def produce_message(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.msg

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}("
            f"msg={self.msg!r}, category={self.category!r}, "
            f"level={self.level!r}, extra={self.extra!r})"
        )
