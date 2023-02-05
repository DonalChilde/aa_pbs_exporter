####################################################
#                                                  #
#       src/snippets/string/indexed_string.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-02T07:34:02-07:00            #
# Last Modified: 2023-02-05T13:07:21.336752+00:00  #
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
        return f"{self.idx}: {self.txt!r}"
