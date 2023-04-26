from uuid import uuid5

from aa_pbs_exporter import PROJECT_NAMESPACE

PARSER_VERSION = "pilot_pbs_2022_01"
PARSER_DNS = uuid5(PROJECT_NAMESPACE, PARSER_VERSION)
