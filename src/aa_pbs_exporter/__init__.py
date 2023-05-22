"""Top-level package for aa_pbs_exporter."""
from uuid import NAMESPACE_DNS, uuid5

from aa_pbs_exporter.airports import Airport, load

PROJECT_NAMESPACE = uuid5(NAMESPACE_DNS, f"pfmsoft.{__name__}")
PROJECT_SLUG = __name__


airports_iata = load("IATA")
