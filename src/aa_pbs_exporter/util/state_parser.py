####################################################
#                                                  #
#          src/snippets/parsing/parser.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-31T14:54:41-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from pathlib import Path
from typing import Iterable, Sequence

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Parser:
    def parse(self, line_number: int, line: str, ctx) -> str:
        """Implement parsing of a particular line here

        returns a string representing the new state of the parse job.
        ctx can be used to aggregate parsed data, and pass extra info needed for
        a future parse attempt.
        """
        raise NotImplementedError


class ParseScheme:
    """Contains the parse scheme"""

    def expected(self, state: str) -> Sequence[Parser]:
        """return list of expected Parsers based on the current state."""
        raise NotImplementedError


class ParseException(Exception):
    """Use this exception to signal a failed parse."""


def parse_file(file_path: Path, scheme: ParseScheme, ctx, skip_blank: bool = True):
    with open(file_path, encoding="utf-8") as file:
        parse_lines(file, scheme=scheme, ctx=ctx, skip_blank=skip_blank)


def parse_lines(
    lines: Iterable[str], scheme: ParseScheme, ctx, skip_blank: bool = True
):
    state = "start"
    for line_number, line in enumerate(lines):
        if skip_blank:
            if not line.strip():
                continue
        try:
            state = parse_line(line_number, line, scheme.expected(state), ctx)
        except ParseException as error:
            logger.error("%s", error)


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
