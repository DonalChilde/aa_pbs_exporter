####################################################
#                                                  #
#  src/snippets/datetime/parse_duration_regex.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-09-28T17:11:31-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

"""
Various duration parsing strategies using regex.
"""

import re

from .factored_duration import FactoredDuration

HHH = r"(?P<hours>[0-9]+([,.][0-9]+)?)"
MM = r"(?P<minutes>[0-5][0-9])"
SS = r"(?P<seconds>[0-5][0-9])"
FS = r"(?P<fractional_seconds>([0-9]+))"


# FIXME handle commas in matches better, eg. 2,750


def parse_duration(pattern: re.Pattern, duration_string: str) -> FactoredDuration:
    """
    Parse a duration string

    Supports hours minutes seconds and fractional seconds.

    Args:
        pattern: the re pattern used to parse the duration
        duration_string: The duration string to be parsed.

    Raises:
        ValueError: Exception if pattern does not match

    Returns:
        a timedelta for the duration string.
    """
    result = pattern.match(duration_string)
    if not result:
        raise ValueError(f"{duration_string} does not match pattern {pattern.pattern}")
    match_dict = result.groupdict()
    possible_groups = [
        "years",
        "days",
        "hours",
        "minutes",
        "seconds",
        "fractional_seconds",
    ]
    for unit in possible_groups:
        if unit not in match_dict or match_dict[unit] is None:
            match_dict[unit] = "0"
        match_dict[unit] = match_dict[unit].replace(",", "").replace(".", "")
    dur = FactoredDuration(
        years=int(match_dict["years"]),
        days=int(match_dict["days"]),
        hours=int(match_dict["hours"]),
        minutes=int(match_dict["minutes"]),
        seconds=int(match_dict["seconds"]),
        fractional_seconds=int(match_dict["fractional_seconds"]),
        fractional_exponent=len(match_dict["fractional_seconds"]),
    )

    return dur


def pattern_HHHMMSSFS(
    hm_sep: str = ":", ms_sep: str = ":", fs_sep: str = "."
) -> re.Pattern:
    """
    Parse a string duration of the pattern HHHMMSSFS.

    Some valid formats:
    0:00:01
    123:14:35
    123:15:34.456

    _extended_summary_

    Args:
        hm_sep: _description_. Defaults to ":".
        ms_sep: _description_. Defaults to ":".
        fs_sep: _description_. Defaults to ".".

    Returns:
        _description_
    """
    pattern_string = rf"{HHH}{hm_sep}{MM}{ms_sep}{SS}({fs_sep}{FS})?"
    return re.compile(pattern_string)


def pattern_HHHMM(hm_sep: str = ":") -> re.Pattern:
    pattern_string = rf"{HHH}{hm_sep}{MM}"
    return re.compile(pattern_string)
