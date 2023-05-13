from datetime import datetime, timedelta, timezone


def add_timedelta(
    ref_datetime: datetime, t_delta: timedelta, *, utc_out: bool = False
) -> datetime:
    # TODO make snippet
    """
    Combine an aware datetime with a timedelta. Enforce utc manipulation.

    _extended_summary_

    Args:
        ref_datetime: _description_
        t_delta: _description_
        utc_out: _description_. Defaults to False.

    Raises:
        ValueError: _description_

    Returns:
        _description_
    """
    if ref_datetime.tzinfo is None:
        raise ValueError(
            f"ref_datetime: {ref_datetime!r} must be tz aware. No tzinfo found"
        )
    ref_tz = ref_datetime.tzinfo
    utc_ref = ref_datetime.astimezone(timezone.utc)
    utc_delta = utc_ref + t_delta
    if utc_out:
        return utc_delta
    return utc_delta.astimezone(ref_tz)
