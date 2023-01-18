"""Top-level package for aa_pbs_exporter."""
from uuid import uuid5, NAMESPACE_DNS

PROJECT_NAMESPACE = uuid5(NAMESPACE_DNS, f"pfmsoft.{__name__}")
