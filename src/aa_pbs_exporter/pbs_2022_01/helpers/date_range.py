from datetime import date, datetime
from typing import Iterable


def date_range(
    start_date: date | datetime, end_date: date | datetime, inclusive: bool = True
) -> Iterable[date]:
    # TODO move to snippets
    # TODO make uasable forwards and backwards, right now assumes forwards
    # https://stackoverflow.com/a/32616832/105844
    if inclusive:
        extra = 1
    else:
        extra = 0
    for ordinal in range(start_date.toordinal(), end_date.toordinal() + extra):
        yield date.fromordinal(ordinal)
