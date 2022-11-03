from datetime import datetime

import airportsdata

from aa_pbs_exporter.airports.airport_model import Airport, generate_airport_uuid

airports_iata = airportsdata.load("iata")


def by_iata(iata: str, effective: datetime | None = None) -> Airport:
    _ = effective
    raw_airport = airports_iata.get(iata, None)
    if raw_airport is None:
        raise ValueError(f"iata code {iata} not found in database.")
    airport = Airport(
        ident=generate_airport_uuid(raw_airport),
        icao=raw_airport["icao"],
        iata=raw_airport["iata"],
        name=raw_airport["name"],
        city=raw_airport["city"],
        subd=raw_airport["subd"],
        country=raw_airport["country"],
        elevation=int(raw_airport["elevation"]),
        lat=raw_airport["lat"],
        lon=raw_airport["lon"],
        tz=raw_airport["tz"],
        effective=None,
    )
    return airport
