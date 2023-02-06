####################################################
#                                                  #
#  src/snippets/string/indexed_string_protocol.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-02-05T06:05:14-07:00            #
# Last Modified: 2023-02-05T13:07:21.338415+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Protocol


class IndexedStringProtocol(Protocol):
    idx: int
    txt: str
