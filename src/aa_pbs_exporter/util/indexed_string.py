####################################################
#                                                  #
#       src/snippets/string/indexed_string.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-02T07:34:02-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import NamedTuple


class IndexedString(NamedTuple):
    idx: int
    str_value: str
