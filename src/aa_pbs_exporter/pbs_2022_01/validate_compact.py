from aa_pbs_exporter.pbs_2022_01.models import compact, raw


def validate_trip(raw_trip: raw.Trip, compact_trip: compact.Trip, ctx: dict):
    pass


# pass in temp variables like len(date_range) via ctx
# compact model is validated just before returning created objects.
