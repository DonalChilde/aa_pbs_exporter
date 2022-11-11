from dataclasses import dataclass


@dataclass
class LineReference:
    source: str
    from_line: int
    to_line: int
