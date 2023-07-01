from typing import Any, Dict, Sequence

from aa_pbs_exporter.pbs_2022_01.parser import parsers_td as parsers
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
)


def parse_scheme() -> Dict[str, Sequence[IndexedStringParserProtocol]]:
    scheme = {
        "start": [
            parsers.PageHeader1(),
        ],
        "PageHeader1": [
            parsers.PageHeader2(),
        ],
        "PageHeader2": [
            parsers.HeaderSeparator(),
        ],
        "HeaderSeparator": [
            parsers.TripHeader(),
            parsers.BaseEquipment(),
        ],
        "BaseEquipment": [
            parsers.TripHeader(),
        ],
        "TripHeader": [
            parsers.DutyPeriodReport(),
            parsers.PriorMonthDeadhead(),
        ],
        "PriorMonthDeadhead": [
            parsers.DutyPeriodReport(),
        ],
        "DutyPeriodReport": [
            parsers.Flight(),
            parsers.FlightDeadhead(),
        ],
        "Flight": [
            parsers.Flight(),
            parsers.FlightDeadhead(),
            parsers.DutyPeriodRelease(),
        ],
        "DutyPeriodRelease": [
            parsers.Hotel(),
            parsers.TripFooter(),
        ],
        "Hotel": [
            parsers.Transportation(),
            parsers.DutyPeriodReport(),
            parsers.HotelAdditional(),
        ],
        "Transportation": [
            parsers.DutyPeriodReport(),
            parsers.HotelAdditional(),
        ],
        "HotelAdditional": [
            parsers.DutyPeriodReport(),
            parsers.TransportationAdditional(),
        ],
        "TransportationAdditional": [
            parsers.DutyPeriodReport(),
            parsers.HotelAdditional(),
        ],
        "TripFooter": [
            parsers.TripSeparator(),
            parsers.CalendarOnly(),
        ],
        "CalendarOnly": [
            parsers.TripSeparator(),
        ],
        "TripSeparator": [
            parsers.TripHeader(),
            parsers.PageFooter(),
        ],
        "PageFooter": [
            parsers.PageHeader1(),
        ],
    }
    return scheme


PARSE_SCHEME: Dict[str, Sequence[IndexedStringParserProtocol]] = parse_scheme()


def parser_lookup(key: str) -> Sequence[IndexedStringParserProtocol]:
    return PARSE_SCHEME[key]


class ParserLookupSingle:
    """Always returns a list containing only the specified parser"""

    def __init__(self, parser: IndexedStringParserProtocol) -> None:
        self.parser = parser

    def __call__(self, key: str) -> Sequence[IndexedStringParserProtocol]:
        return [self.parser]
