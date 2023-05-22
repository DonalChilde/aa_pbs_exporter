#!/usr/bin/env python3

"""
Extensive database of location and timezone data for nearly every airport and landing strip in the world.

Forked from https://github.com/mborsetti/airportsdata
"""


import csv
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Dict, Literal


@dataclass
class Airport:
    icao: str
    iata: str
    name: str
    city: str
    subd: str
    country: str
    elevation: float
    lat: str
    lon: str
    tz: str
    lid: str


CodeType = Literal["ICAO", "IATA", "LID"]


def load(code_type: CodeType = "ICAO") -> Dict[str, "Airport"]:
    """Loads airport data into a dict

    :param code_type: optional argument defining the key in the dictionary: 'ICAO' (default if omitted),
    'IATA' (for IATA Location Codes) or 'LID' (for U.S. FAA Location Identifiers).

    :return: a dict of dicts, each entry having the following keys:
        'icao': ICAO 4-letter Location Indicator or 4-alphanumeric FAA/TC LID
        'iata': IATA 3-letter Location Code or an empty string
        'name': Official name (latin script)
        'city': City
        'subd': Subdivision (e.g. state, province, region, etc.)
        'country': ISO 3166-1 alpha 2-code (plus 'XK' for Kosovo)
        'elevation': MSL elevation (the highest point of the landing area) in feet
        'lat': Latitude (decimal)
        'lon': Longitude (decimal)
        'tz': Timezone expressed as a tz database name (IANA-compliant) or empty string for country 'AQ' (Antarctica).
            Originally sourced from [TimeZoneDB](https://timezonedb.com)
        'lid': The FAA Location Identifier (for US country only; others is blank)
    """

    key = code_type.lower()
    if key not in ("icao", "iata", "lid"):
        raise ValueError(
            f"code_type must be one of ICAO, IATA or LID; received {code_type}"
        )
    # this_dir = Path(__file__).parent
    this_dir = resources.files(__package__)
    airports: Dict[str, Airport] = {}
    with this_dir.joinpath("airports.csv").open(encoding="utf8") as f:
        reader = csv.DictReader(f, quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            row["elevation"] = float(row["elevation"])
            airports[row[key]] = Airport(**row)  # type: ignore
    airports.pop("", None)
    return airports


# Python 3.9 code used to save the dict to CSV:
# with open('airports.csv', 'w', newline='') as f:
#     fieldnames = airports[list(airports.keys())[0]].keys()
#     writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
#     writer.writeheader()
#     for data in airports.values():
#         writer.writerow(data)
