from datetime import time


def compare_time(time_1: time, time_2: time, ignore_tz: bool = False) -> bool:
    # TODO make snippet
    if ignore_tz:
        naive_time_1 = time_1.replace(tzinfo=None)
        naive_time_2 = time_2.replace(tzinfo=None)
        return naive_time_1 == naive_time_2
    return time_1 == time_2
