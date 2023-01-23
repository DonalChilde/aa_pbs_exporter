import hashlib
from datetime import datetime
from uuid import NAMESPACE_DNS, UUID, uuid5

from pydantic import BaseModel

PROJECT_NAMESPACE = uuid5(NAMESPACE_DNS, "pfmsoft.airportsdata")


def generate_airport_uuid(values: dict):
    hasher = hashlib.sha3_512()
    for key, value in values.items():
        # TODO make this more deterministic
        _ = key
        hasher.update(str(value).encode("utf-8"))
    result = uuid5(PROJECT_NAMESPACE, hasher.hexdigest())
    return result


class Airport(BaseModel):
    ident: UUID
    icao: str
    iata: str
    name: str
    city: str
    subd: str
    country: str
    elevation: int
    lat: str
    lon: str
    tz: str
    effective: datetime | None
