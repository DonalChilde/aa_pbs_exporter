from datetime import time


def compare_time(time_1: time, time_2: time, ignore_tz: bool = False) -> bool:
    # TODO make snippet
    if ignore_tz:
        nieve_time_1 = time_1.replace(tzinfo=None)
        nieve_time_2 = time_2.replace(tzinfo=None)
        return nieve_time_1 == nieve_time_2
    return time_1 == time_2
