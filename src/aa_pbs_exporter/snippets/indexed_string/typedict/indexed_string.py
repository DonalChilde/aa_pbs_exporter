####################################################
#                                                  #
#  src/snippets/indexed_string/typedict/indexed_string.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-06-26T14:26:13-07:00            #
# Last Modified: 2023-06-26T23:11:51.056853+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import TypedDict


class IndexedString(TypedDict):
    idx: int
    txt: str
