# from datetime import datetime


# from aa_pbs_exporter.airports import load, Airport

# airports_iata = load("IATA")


# def by_iata(iata: str, effective: datetime | None = None) -> Airport:
#     _ = effective
#     raw_airport = airports_iata.get(iata, None)
#     if raw_airport is None:
#         raise ValueError(f"iata code {iata} not found in database.")
#     airport = Airport(
#         ident=generate_airport_uuid(raw_airport),
#         icao=raw_airport["icao"],
#         iata=raw_airport["iata"],
#         name=raw_airport["name"],
#         city=raw_airport["city"],
#         subd=raw_airport["subd"],
#         country=raw_airport["country"],
#         elevation=int(raw_airport["elevation"]),
#         lat=raw_airport["lat"],
#         lon=raw_airport["lon"],
#         tz=raw_airport["tz"],
#         effective=None,
#     )
#     return airport


# def tz_name_from_iata(iata: str) -> str:
#     raw_airport = airports_iata.get(iata, None)
#     if raw_airport is None:
#         raise ValueError(f"iata code {iata} not found in database.")
#     return raw_airport["tz"]
