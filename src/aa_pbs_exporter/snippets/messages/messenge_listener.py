####################################################
#                                                  #
#       src/snippets/messages/messenger.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-04-26T11:15:26-07:00            #
# Last Modified: 2023-05-22T17:42:40.603572+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from io import TextIOWrapper
from typing import Callable

from . import Message


class MessengeListener:
    def __init__(
        self,
        *,
        sieve: Callable[[Message], bool] | None = None,
        formatter: Callable[[Message], str] | None = None,
    ) -> None:
        self.sieve = sieve
        self.formatter = formatter

    def receive_message(self, msg: Message):
        raise NotImplementedError

    def format_message(self, msg: Message) -> str:
        if self.formatter is None:
            return msg.produce_message()
        return self.formatter(msg)

    def filter_message(self, msg: Message) -> bool:
        if self.sieve is None:
            return True
        return self.sieve(msg)


class PrintMessengeListener(MessengeListener):
    def __init__(
        self,
        *,
        sieve: Callable[[Message], bool] | None = None,
        formatter: Callable[[Message], str] | None = None,
        end: str = "\n",
        file: TextIOWrapper | None = None,
        flush: bool = False,
    ) -> None:
        super().__init__(sieve=sieve, formatter=formatter)
        self.end = end
        self.file = file
        self.flush = flush

    def receive_message(self, msg: Message):
        if self.filter_message(msg=msg):
            msg_txt = self.format_message(msg)
            print(
                msg_txt,
                end=self.end,
                file=self.file,
                flush=self.flush,
            )


def category_sieve(txt: str) -> Callable[[Message], bool]:
    def sieve(msg: Message) -> bool:
        if txt in msg.category:
            return True
        return False

    return sieve
