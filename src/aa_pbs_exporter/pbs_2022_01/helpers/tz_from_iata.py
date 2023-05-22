from aa_pbs_exporter import airports_iata


def tz_from_iata(iata: str) -> str:
    raw_airport = airports_iata.get(iata, None)
    if raw_airport is None:
        raise ValueError(f"iata code {iata} not found in database.")
    return raw_airport.tz
