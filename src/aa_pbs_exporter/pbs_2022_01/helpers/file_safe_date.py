from datetime import datetime


def file_safe_date(value: datetime) -> str:
    if value.tzinfo:
        return value.strftime("%Y%m%d_%H%M%S_%f_%z")
    return value.strftime("%Y%m%d_%H%M%S_%f")
