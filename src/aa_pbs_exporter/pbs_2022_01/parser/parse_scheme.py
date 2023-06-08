from typing import Dict, Sequence

from aa_pbs_exporter.pbs_2022_01.parser.parsers import (
    BaseEquipment,
    CalendarOnly,
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
    PriorMonthDeadhead,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    IndexedStringParserProtocol,
)


def parse_scheme() -> Dict[str, Sequence[IndexedStringParserProtocol]]:
    scheme = {
        "start": [PageHeader1()],
        "page_header_1": [PageHeader2()],
        "page_header_2": [HeaderSeparator()],
        "header_separator": [TripHeader(), BaseEquipment()],
        "base_equipment": [TripHeader()],
        "trip_header": [DutyPeriodReport(), PriorMonthDeadhead()],
        "prior_month_deadhead": [DutyPeriodReport()],
        "dutyperiod_report": [Flight(), FlightDeadhead()],
        "flight": [Flight(), FlightDeadhead(), DutyPeriodRelease()],
        "dutyperiod_release": [Hotel(), TripFooter()],
        "hotel": [Transportation(), DutyPeriodReport(), HotelAdditional()],
        "transportation": [DutyPeriodReport(), HotelAdditional()],
        "hotel_additional": [DutyPeriodReport(), TransportationAdditional()],
        "transportation_additional": [DutyPeriodReport(), HotelAdditional()],
        "trip_footer": [TripSeparator(), CalendarOnly()],
        "calendar_only": [TripSeparator()],
        "trip_separator": [TripHeader(), PageFooter()],
        "page_footer": [PageHeader1()],
    }
    return scheme
