####################################################
#                                                  #
# src/snippets/parsing/indexed_string_filter.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-10T15:27:45-07:00            #
# Last Modified: 2022-12-03T23:51:03.921172+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Callable, Sequence

from .indexed_string import IndexedString


class SkipBlankLines:
    def __call__(self, indexed_string: IndexedString) -> bool:
        return bool(indexed_string.txt.strip())


class SkipTillMatch:
    def __init__(self, matcher: Callable[[IndexedString], bool]) -> None:
        self.matcher = matcher
        self.procede = False

    def __call__(self, indexed_string: IndexedString) -> bool:
        if self.procede:
            return True
        if self.matcher(indexed_string):
            self.procede = True
            return True
        return False


class MultiTest:
    def __init__(self, testers: Sequence[Callable[[IndexedString], bool]]) -> None:
        self.testers: Sequence[Callable[[IndexedString], bool]] = list(testers)

    def __call__(self, indexed_string: IndexedString) -> bool:
        return all((tester(indexed_string) for tester in self.testers))
