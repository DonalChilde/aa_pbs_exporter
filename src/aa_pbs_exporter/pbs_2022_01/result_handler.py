from uuid import uuid5
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseResultProtocol,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.result_handler import (
    ParseResultHandler,
    ParseResultToFile,
)
from aa_pbs_exporter.pbs_2022_01.parse_result import ParseResult


class AssembleRawBidPackage(ParseResultHandler):
    def __init__(self, source: str) -> None:
        super().__init__()
        self.source = source
        uuid = uuid5(raw.BIDPACKAGE_DNS, source)
        self.bid_package = raw.BidPackage(uuid=uuid, source=source, pages=[])

    def handle_result(
        self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
    ):
        _ = kwargs, ctx
        match_value = parse_result.parsed_data.__class__.__qualname__
        match match_value:
            case "PageHeader1":
                assert isinstance(parse_result.parsed_data, raw.PageHeader1)
                data = parse_result.parsed_data
                self.bid_package.pages.append(
                    raw.Page(uuid=data.uuid5(), page_header_1=data, trips=[])
                )
            case "PageHeader2":
                assert isinstance(parse_result.parsed_data, raw.PageHeader2)
                self.bid_package.pages[-1].page_header_2 = parse_result.parsed_data
            case "HeaderSeparator":
                pass
            case "BaseEquipment":
                assert isinstance(parse_result.parsed_data, raw.BaseEquipment)
                self.bid_package.pages[-1].base_equipment = parse_result.parsed_data
            case "TripHeader":
                assert isinstance(parse_result.parsed_data, raw.TripHeader)
                data = parse_result.parsed_data
                self.bid_package.pages[-1].trips.append(
                    raw.Trip(uuid=data.uuid5(), header=data, dutyperiods=[])
                )
            case "DutyPeriodReport":
                assert isinstance(parse_result.parsed_data, raw.DutyPeriodReport)
                data = parse_result.parsed_data
                self.bid_package.pages[-1].trips[-1].dutyperiods.append(
                    raw.DutyPeriod(uuid=data.uuid5(), report=data, flights=[])
                )
            case "Flight":
                assert isinstance(parse_result.parsed_data, raw.Flight)
                self.bid_package.pages[-1].trips[-1].dutyperiods[-1].flights.append(
                    parse_result.parsed_data
                )
            case "DutyPeriodRelease":
                assert isinstance(parse_result.parsed_data, raw.DutyPeriodRelease)
                self.bid_package.pages[-1].trips[-1].dutyperiods[
                    -1
                ].release = parse_result.parsed_data
            case "Hotel":
                assert isinstance(parse_result.parsed_data, raw.Hotel)
                data = parse_result.parsed_data
                layover = raw.Layover(uuid=data.uuid5(), hotel=data)
                self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover = layover
            case "HotelAdditional":
                assert isinstance(parse_result.parsed_data, raw.HotelAdditional)
                assert (
                    self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                    is not None
                )
                layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover

                layover.hotel_additional = parse_result.parsed_data
            case "Transportation":
                assert isinstance(parse_result.parsed_data, raw.Transportation)
                assert (
                    self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                    is not None
                )
                layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                layover.transportation = parse_result.parsed_data
            case "TransportationAdditional":
                assert isinstance(
                    parse_result.parsed_data, raw.TransportationAdditional
                )
                assert (
                    self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                    is not None
                )
                layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
                layover.transportation_additional = parse_result.parsed_data
            case "TripFooter":
                assert isinstance(parse_result.parsed_data, raw.TripFooter)
                self.bid_package.pages[-1].trips[-1].footer = parse_result.parsed_data
            case "TripSeparator":
                # could validate trip here
                pass
            case "PageFooter":
                assert isinstance(parse_result.parsed_data, raw.PageFooter)
                # could validate page here
                self.bid_package.pages[-1].page_footer = parse_result.parsed_data

    def finalize(self, ctx: dict | None = None):
        return super().finalize(ctx)
        # TODO ensure final validation here?


class DebugToFile(ParseResultToFile):

    def result_to_txt(
        self, parse_result: ParseResult, ctx: dict | None = None, **kwargs
    ) -> str:
        return f"{parse_result}"
