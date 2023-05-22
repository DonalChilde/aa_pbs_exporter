from datetime import datetime, time


def complete_time(
    ref_datetime: datetime, new_time: time, is_future: bool = True
) -> datetime:
    """
    Find the next datetime with new_time, either future or past.

    Assume both values have tzinfo so that can compare times.

    Args:
        ref_datetime: _description_
        new_time: _description_
        is_future: _description_. Defaults to True.

    Raises:
        ValueError: _description_
        ValueError: _description_

    Returns:
        _description_
    """
    # TODO make snippet

    if ref_datetime.tzinfo is None:
        raise ValueError(f"ref_datetime {ref_datetime!r} must have tzinfo.")
    if new_time.tzinfo is None:
        raise ValueError(f"new_time {new_time!r} must have tzinfo")
    shifted_datetime = ref_datetime.astimezone(new_time.tzinfo)
    if is_future:
        if shifted_datetime.time() < new_time:
            return datetime.combine(shifted_datetime.date(), new_time)
        shifted_date = datetime.fromordinal(shifted_datetime.date().toordinal() + 1)
        return datetime.combine(shifted_date, new_time)
    if shifted_datetime.time() > new_time:
        return datetime.combine(shifted_datetime.date(), new_time)
    shifted_date = datetime.fromordinal(shifted_datetime.date().toordinal() - 1)
    return datetime.combine(shifted_date, new_time)
