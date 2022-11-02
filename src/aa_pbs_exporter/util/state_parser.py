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

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SkipBlankLines:
    def __call__(self, index: str, line: str) -> bool:
        return bool(line.strip())


class SkipTillMatch:
    def __init__(self, matcher: Callable[[str, str], bool]) -> None:
        self.matcher = matcher
        self.procede = False

    def __call__(self, index: str, line: str) -> bool:
        if self.procede:
            return True
        if self.matcher(index, line):
            self.procede = True
            return True
        return False


class MultiTest:
    def __init__(self, testers: Sequence[Callable[[str, str], bool]]) -> None:
        self.testers: Sequence[Callable[[str, str], bool]] = list(testers)

    def __call__(self, index: str, line: str) -> bool:
        return all((tester(index, line) for tester in self.testers))


class Parser:
    def parse(self, line_number: int, line: str, ctx) -> str:
        """Implement parsing of a particular line here

        returns a string representing the new state of the parse job.
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
    skipper: Callable[[str, str], bool] | None = None,
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
    skipper: Callable[[str, str], bool] | None = None,
):
    state = "start"
    for line_number, line in enumerate(lines):
        if skipper is not None and not skipper(str(line_number), line):
            continue
        try:
            state = parse_line(line_number, line, scheme.expected(state), ctx)
        except ParseException as error:
            logger.error("%s", error)
            raise error


def parse_line(line_number: int, line: str, parsers: Sequence[Parser], ctx) -> str:
    for parser in parsers:
        try:
            new_state = parser.parse(line_number=line_number, line=line, ctx=ctx)
            logger.info(
                "\n\t%s: PARSED %r: %r", line_number, parser.__class__.__name__, line
            )
            return new_state
        except ParseException as error:
            logger.info(
                "\n\t%s: FAILED %r: %r\n\t%r",
                line_number,
                parser.__class__.__name__,
                line,
                error,
            )
    raise ParseException(
        f"No parser found for {line_number}: {line}\nTried {parsers!r}"
    )
