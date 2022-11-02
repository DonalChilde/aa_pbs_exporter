####################################################
#                                                  #
#   src/snippets/string/index_numeric_strings.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-02T07:27:43-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Iterable, Iterator

from .indexed_string import IndexedString


def index_numeric_strings(string_values: Iterable[str]) -> Iterator[IndexedString]:
    for idx, item in enumerate(string_values):
        if item.isnumeric():
            yield IndexedString(idx, item)
