"""Top-level package for aa_pbs_exporter."""
from uuid import NAMESPACE_DNS, uuid5

PROJECT_NAMESPACE = uuid5(NAMESPACE_DNS, f"pfmsoft.{__name__}")
PROJECT_SLUG = __name__
