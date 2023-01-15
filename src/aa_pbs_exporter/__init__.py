"""Top-level package for aa_pbs_exporter."""
from uuid import uuid5, NAMESPACE_DNS
import logging

logger = logging.getLogger(__name__)


__author__ = """Chad Lowe"""
__email__ = "pfmsoft@gmail.com"
# The short X.Y.Z version.
__version__ = "0.1.0"
# The full version, including alpha/beta/rc tags.
__release__ = __version__


# Prefer caps vs underscore?
# Not all of these may be useful as variables...

# PROJECT_SLUG should be the name of the top level package.
PROJECT_SLUG = __name__
PROJECT_NAME = "aa-pbs-exporter"
PROJECT_CLI = "aa-pbs-exporter"
PROJECT_NAMESPACE = uuid5(NAMESPACE_DNS, f"pfmsoft.{PROJECT_SLUG}")

AUTHOR = """Chad Lowe"""
EMAIL = "pfmsoft@gmail.com"
# The short X.Y.Z version.
VERSION = "0.1.0"
# The full version, including alpha/beta/rc tags.
RELEASE = VERSION
