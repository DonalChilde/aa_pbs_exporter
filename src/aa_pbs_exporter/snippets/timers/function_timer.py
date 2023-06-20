####################################################
#                                                  #
#      src/snippets/timers/function_timer.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-06-19T07:38:54-07:00            #
# Last Modified: 2023-06-19T17:48:08.550488+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

import logging
from functools import wraps
from time import perf_counter_ns

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

NANOS_PER_SECOND = 1000000000


def function_timer(
    func,
    logger: logging.Logger | None = None,
    level: int = logging.DEBUG,
    repr_length: int = 100,
):
    """Log the time it takes to run a function."""
    if logger is None:
        logger = _logger

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter_ns()
        result = func(*args, **kwargs)
        end = perf_counter_ns()
        if repr_length == -1:
            logger.log(
                level,
                "%s ran in %ss with args: %s",
                func.__name__,
                f"{(end-start)/NANOS_PER_SECOND:9f}",
                repr((args, kwargs)),
            )
            return result
        if repr_length > 0:
            logger.log(
                level,
                "%s ran in %ss with args: %s",
                func.__name__,
                f"{(end-start)/NANOS_PER_SECOND:9f}",
                repr((args, kwargs))[:repr_length],
            )
            return result
        logger.log(
            level, "%s ran in %ss", func.__name__, f"{(end-start)/NANOS_PER_SECOND:9f}"
        )
        return result

    return wrapper
