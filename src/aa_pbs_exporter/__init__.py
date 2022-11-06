"""Top-level package for aa_pbs_exporter."""
from uuid import uuid5, NAMESPACE_DNS

__author__ = """Chad Lowe"""
__email__ = "pfmsoft@gmail.com"
# The short X.Y.Z version.
__version__ = "0.1.0"
# The full version, including alpha/beta/rc tags.
__release__ = __version__

PROJECT_NAMESPACE = uuid5(NAMESPACE_DNS, "pfmsoft.aa_pbs_exporter")
