####################################################
#                                                  #
# src/snippets/indexed_string/typedict/filters.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-10T15:27:45-07:00            #
# Last Modified: 2023-06-26T23:11:51.058100+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Callable, Sequence

from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
)


class SkipTillFirstMatch:
    """
    Skip until first match found.

    """

    def __init__(self, match_test: Callable[[IndexedString], bool]) -> None:
        self.match_test = match_test
        self.procede = False

    def __call__(self, indexed_string: IndexedString) -> bool:
        if self.procede:
            return True
        if self.match_test(indexed_string):
            self.procede = True
            return True
        return False


class MultipleTests:
    """Test for multiple conditions."""

    def __init__(self, testers: Sequence[Callable[[IndexedString], bool]]) -> None:
        self.testers: Sequence[Callable[[IndexedString], bool]] = list(testers)

    def __call__(self, indexed_string: IndexedString) -> bool:
        return all((tester(indexed_string) for tester in self.testers))


def is_numeric(indexed_string: IndexedString) -> bool:
    """String can be a number."""
    return indexed_string["txt"].isnumeric()


def is_whitespace(indexed_string: IndexedString) -> bool:
    """String contains only white space"""
    return indexed_string["txt"].isspace()


def not_white_space(indexed_string: IndexedString) -> bool:
    """String does not contain only white space."""
    return not is_whitespace(indexed_string)


def pass_through(indexed_string: IndexedString) -> bool:
    """True for all strings."""
    _ = indexed_string
    return True
