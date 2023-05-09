from typing import Dict, Sequence

from aa_pbs_exporter.pbs_2022_01.parser.parsers import (
    BaseEquipment,
    DutyPeriodRelease,
    DutyPeriodReport,
    Flight,
    FlightDeadhead,
    HeaderSeparator,
    Hotel,
    HotelAdditional,
    PageFooter,
    PageHeader1,
    PageHeader2,
    Transportation,
    TransportationAdditional,
    TripFooter,
    TripHeader,
    TripSeparator,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
)

PARSE_SCHEME: Dict[str, Sequence[IndexedStringParserProtocol]] = {
    "start": [PageHeader1()],
    "page_header_1": [PageHeader2()],
    "page_header_2": [HeaderSeparator()],
    "header_separator": [TripHeader(), BaseEquipment()],
    "base_equipment": [TripHeader()],
    "trip_header": [DutyPeriodReport()],
    "dutyperiod_report": [Flight(), FlightDeadhead()],
    "flight": [Flight(), FlightDeadhead(), DutyPeriodRelease()],
    "dutyperiod_release": [Hotel(), TripFooter()],
    "hotel": [Transportation(), DutyPeriodReport(), HotelAdditional()],
    "transportation": [DutyPeriodReport(), HotelAdditional()],
    "hotel_additional": [TransportationAdditional()],
    "transportation_additional": [DutyPeriodReport()],
    "trip_footer": [TripSeparator()],
    "trip_separator": [TripHeader(), PageFooter()],
    "page_footer": [PageHeader1()],
}


def parse_scheme() -> Dict[str, Sequence[IndexedStringParserProtocol]]:
    scheme = {
        "start": [PageHeader1()],
        "page_header_1": [PageHeader2()],
        "page_header_2": [HeaderSeparator()],
        "header_separator": [TripHeader(), BaseEquipment()],
        "base_equipment": [TripHeader()],
        "trip_header": [DutyPeriodReport()],
        "dutyperiod_report": [Flight(), FlightDeadhead()],
        "flight": [Flight(), FlightDeadhead(), DutyPeriodRelease()],
        "dutyperiod_release": [Hotel(), TripFooter()],
        "hotel": [Transportation(), DutyPeriodReport(), HotelAdditional()],
        "transportation": [DutyPeriodReport(), HotelAdditional()],
        "hotel_additional": [TransportationAdditional()],
        "transportation_additional": [DutyPeriodReport()],
        "trip_footer": [TripSeparator()],
        "trip_separator": [TripHeader(), PageFooter()],
        "page_footer": [PageHeader1()],
    }
    return scheme
