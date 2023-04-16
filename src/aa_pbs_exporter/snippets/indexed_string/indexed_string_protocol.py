####################################################
#                                                  #
# src/snippets/indexed_string/indexed_string_protocol.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-02-05T06:05:14-07:00            #
# Last Modified: 2023-04-15T23:08:58.644236+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Protocol


class IndexedStringProtocol(Protocol):
    idx: int
    txt: str
