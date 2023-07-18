from logging import Logger

import pyparsing as pp

DASH_UNICODE = "-\u002d\u2212"
CALENDAR_ENTRY = pp.Or(
    [
        pp.Word(DASH_UNICODE, exact=2, as_keyword=True),
        pp.Word(pp.nums, exact=1, as_keyword=True),
        pp.Word(pp.nums, exact=2, as_keyword=True),
    ]
)
DASH_ENTRY = pp.Word(DASH_UNICODE, exact=2, as_keyword=True)

DASH_WORD = pp.Word("\u2212", exact=2)("result")
CALDENDAR_LINE = "                                                                                       −− 17 18 19 20 21 22"
DASH = " \u2212\u2212 "
DASH_DAY = pp.Word(DASH_UNICODE, exact=2)
NUMERICAL_DAY = pp.Or(
    [
        pp.Word(pp.nums, exact=1, as_keyword=True),
        pp.Word(pp.nums, exact=2, as_keyword=True),
    ]
)
CALENDAR_DAY = pp.Or([DASH_DAY, NUMERICAL_DAY])
DAYS = " \u2212\u2212 2 23 25 "


def test_match(logger: Logger):
    txt = DAYS
    parser = pp.OneOrMore(CALENDAR_DAY)
    result = parser.parse_string(txt)
    print("Result Dump:\n", result.dump(indent="  "))

    # assert False
