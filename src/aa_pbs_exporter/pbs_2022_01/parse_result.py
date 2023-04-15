from dataclasses import dataclass

from aa_pbs_exporter.pbs_2022_01.models import raw


@dataclass
class ParseResult:
    current_state: str
    parsed_data: raw.ParsedIndexedString
