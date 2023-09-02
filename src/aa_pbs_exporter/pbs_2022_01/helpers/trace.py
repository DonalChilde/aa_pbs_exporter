# TODO make snippet
from functools import wraps


def trace(func):
    """Debug function that prints args and result.

    From Effective Python (?) p. 103
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__}({args!r},{kwargs!r}) -> {result!r}")
        return result

    return wrapper
