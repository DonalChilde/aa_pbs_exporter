from typing import Iterable, Sized


def length(data: Iterable | Sized) -> int:
    # TODO move to a snippets
    try:
        return len(data)
    except Exception as error:  # FIXME what error is this?
        _ = error
        return sum(1 for _ in data)
