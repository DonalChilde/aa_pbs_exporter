####################################################
#                                                  #
#      src/snippets/parsing/indexed_string.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-06T14:16:40-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from dataclasses import dataclass


@dataclass
class IndexedString:
    idx: int
    txt: str

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}(idx={self.idx}, txt={self.txt!r})"

    def __str__(self):
        return f"{self.idx}: {self.txt}"
