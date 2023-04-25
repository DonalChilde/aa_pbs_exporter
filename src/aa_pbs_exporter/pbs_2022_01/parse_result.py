# from dataclasses import dataclass
from pydantic import BaseModel
from aa_pbs_exporter.pbs_2022_01.models import raw
import json

# @dataclass
# class ParseResult:
#     current_state: str
#     parsed_data: raw.ParsedIndexedString


class ParseResult(BaseModel):
    current_state: str
    parsed_data: raw.ParsedIndexedString

    def __str__(self) -> str:
        data = self.parsed_data.dict()
        data.pop("source")
        source = self.parsed_data.source

        return (
            f"{source.idx}:{self.current_state}:{source.uuid5(raw.PARSER_DNS)}:{source.txt!r}"
            f"\n\t{self.parsed_data.__class__.__name__}: {json.dumps(data)}"
        )
