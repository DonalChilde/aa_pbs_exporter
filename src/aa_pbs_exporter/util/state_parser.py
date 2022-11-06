####################################################
#                                                  #
#          src/snippets/parsing/state_parser.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-31T14:54:41-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
from pathlib import Path
from typing import Callable, Iterable, Sequence
from .indexed_string import IndexedString

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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


class Parser:
    def parse(self, indexed_string: IndexedString, ctx) -> str:
        """Implement parsing of a particular line here

        returns a string representing the new state of the parse job, usually a string
        that is used as a key in the ParseScheme.
        ctx can be used to aggregate parsed data, and pass extra info needed for
        a future parse attempt.
        """
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__qualname__}()"


class ParseScheme:
    """Contains the parse scheme"""

    def expected(self, state: str) -> Sequence[Parser]:
        """return list of expected Parsers based on the current state."""
        raise NotImplementedError


class ParseException(Exception):
    """Use this exception to signal a failed parse."""


def parse_file(
    file_path: Path,
    scheme: ParseScheme,
    ctx,
    skipper: Callable[[IndexedString], bool] | None = None,
):
    with open(file_path, encoding="utf-8") as file:
        try:
            parse_lines(file, scheme=scheme, ctx=ctx, skipper=skipper)
        except ParseException as error:
            logger.error("%s Failed to parse %r", file_path, error)
            raise error


def parse_lines(
    lines: Iterable[str],
    scheme: ParseScheme,
    ctx,
    skipper: Callable[[IndexedString], bool] | None = None,
):
    state = "start"
    for line_number, line in enumerate(lines):
        indexed_string = IndexedString(idx=line_number, txt=line)
        if skipper is not None and not skipper(indexed_string):
            continue
        try:
            state = parse_line(
                indexed_string=indexed_string, parsers=scheme.expected(state), ctx=ctx
            )
        except ParseException as error:
            logger.error("%s", error)
            raise error


def parse_line(indexed_string: IndexedString, parsers: Sequence[Parser], ctx) -> str:
    for parser in parsers:
        try:
            new_state = parser.parse(indexed_string=indexed_string, ctx=ctx)
            logger.info("\n\tPARSED %r->%r", parser.__class__.__name__, indexed_string)
            return new_state
        except ParseException as error:
            logger.info(
                "\n\tFAILED %r->%r\n\t%r",
                parser.__class__.__name__,
                indexed_string,
                error,
            )
    raise ParseException(f"No parser found for {indexed_string!r}\nTried {parsers!r}")
