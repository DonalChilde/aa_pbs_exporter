from aa_pbs_exporter.pbs_2022_01.translate.parsed_to_raw import ParsedToRaw
from aa_pbs_exporter.snippets.indexed_string.state_parser.result_handler import (
    ParseResultHandler,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseResultProtocol,
)


class RawResultHandler(ParseResultHandler):
    def __init__(self, translator: ParsedToRaw) -> None:
        super().__init__()
        self.translator = translator

    def handle_result(
        self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
    ):
        _ = kwargs, ctx
        data = parse_result.parsed_data
        match_value = data.__class__.__qualname__
        match match_value:
            case "PageHeader1":
                self.translator.page_header1(data)
            case "PageHeader2":
                self.translator.page_header2(data)
            case "HeaderSeparator":
                self.translator.header_separator(data)
            case "BaseEquipment":
                self.translator.base_equipment(data)
            case "TripHeader":
                self.translator.trip_header(data)
            case "DutyPeriodReport":
                self.translator.duty_period_report(data)
            case "Flight":
                self.translator.flight(data)
            case "DutyPeriodRelease":
                self.translator.duty_period_release(data)
            case "Hotel":
                self.translator.hotel(data)
            case "HotelAdditional":
                self.translator.hotel_additional(data)
            case "Transportation":
                self.translator.transportation(data)
            case "TransportationAdditional":
                self.translator.transportation_additional(data)
            case "CalendarOnly":
                self.translator.calendar_only(data)
            case "TripFooter":
                self.translator.trip_footer(data)
            case "TripSeparator":
                self.translator.trip_separator(data)
            case "PageFooter":
                self.translator.page_footer(data)

    def finalize(self, ctx: dict | None = None):
        self.translator.parse_complete(ctx=ctx)
