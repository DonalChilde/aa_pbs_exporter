NANOS_PER_SECOND = 1000000000


# TODO make snippet
def nanos_to_seconds(start: int, end: int) -> float:
    return (end - start) / NANOS_PER_SECOND
