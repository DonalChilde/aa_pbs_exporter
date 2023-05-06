# from uuid import uuid5

# from aa_pbs_exporter.pbs_2022_01 import PARSER_DNS
# from aa_pbs_exporter.pbs_2022_01.models import raw
# from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
# from aa_pbs_exporter.pbs_2022_01.models.parse_result import ParseResult
# from aa_pbs_exporter.pbs_2022_01.raw_helpers import collect_calendar_entries
# from aa_pbs_exporter.pbs_2022_01.validate_raw import RawValidator
# from aa_pbs_exporter.snippets.indexed_string.state_parser.result_handler import (
#     ParseResultHandler,
#     ParseResultToFile,
# )
# from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
#     ParseResultProtocol,
# )


# class ParsedToRaw(ParseResultHandler):
#     def __init__(
#         self, source: HashedFile | None, validator: RawValidator | None
#     ) -> None:
#         super().__init__()
#         self.source = source
#         self.validator = validator
#         if source:
#             uuid_seed = source.file_hash
#         else:
#             uuid_seed = "None"
#         uuid = uuid5(raw.BIDPACKAGE_DNS, uuid_seed)
#         self.bid_package = raw.BidPackage(uuid=uuid, source=source, pages=[])

#     def handle_result(
#         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
#     ):
#         _ = kwargs, ctx
#         match_value = parse_result.parsed_data.__class__.__qualname__
#         match match_value:
#             case "PageHeader1":
#                 assert isinstance(parse_result.parsed_data, raw.PageHeader1)
#                 data = parse_result.parsed_data
#                 page = raw.Page(uuid=PARSER_DNS, page_header_1=data, trips=[])
#                 page.uuid = page.uuid5()
#                 self.bid_package.pages.append(page)
#             case "PageHeader2":
#                 assert isinstance(parse_result.parsed_data, raw.PageHeader2)
#                 self.bid_package.pages[-1].page_header_2 = parse_result.parsed_data
#             case "HeaderSeparator":
#                 pass
#             case "BaseEquipment":
#                 assert isinstance(parse_result.parsed_data, raw.BaseEquipment)
#                 self.bid_package.pages[-1].base_equipment = parse_result.parsed_data
#             case "TripHeader":
#                 assert isinstance(parse_result.parsed_data, raw.TripHeader)
#                 data = parse_result.parsed_data
#                 trip = raw.Trip(uuid=PARSER_DNS, header=data, dutyperiods=[])
#                 trip.uuid = trip.uuid5()
#                 self.bid_package.pages[-1].trips.append(trip)
#             case "DutyPeriodReport":
#                 assert isinstance(parse_result.parsed_data, raw.DutyPeriodReport)
#                 data = parse_result.parsed_data
#                 dutyperiod = raw.DutyPeriod(uuid=PARSER_DNS, report=data, flights=[])
#                 dutyperiod.uuid = dutyperiod.uuid5()
#                 self.bid_package.pages[-1].trips[-1].dutyperiods.append(dutyperiod)
#             case "Flight":
#                 assert isinstance(parse_result.parsed_data, raw.Flight)
#                 self.bid_package.pages[-1].trips[-1].dutyperiods[-1].flights.append(
#                     parse_result.parsed_data
#                 )
#             case "DutyPeriodRelease":
#                 assert isinstance(parse_result.parsed_data, raw.DutyPeriodRelease)
#                 self.bid_package.pages[-1].trips[-1].dutyperiods[
#                     -1
#                 ].release = parse_result.parsed_data
#             case "Hotel":
#                 assert isinstance(parse_result.parsed_data, raw.Hotel)
#                 data = parse_result.parsed_data
#                 layover = raw.Layover(uuid=PARSER_DNS, hotel=data)
#                 layover.uuid = layover.uuid5()
#                 self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover = layover
#             case "HotelAdditional":
#                 assert isinstance(parse_result.parsed_data, raw.HotelAdditional)
#                 layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
#                 assert layover is not None
#                 layover.hotel_additional = parse_result.parsed_data
#             case "Transportation":
#                 assert isinstance(parse_result.parsed_data, raw.Transportation)
#                 layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
#                 assert layover is not None
#                 layover.transportation = parse_result.parsed_data
#             case "TransportationAdditional":
#                 assert isinstance(
#                     parse_result.parsed_data, raw.TransportationAdditional
#                 )
#                 layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
#                 assert layover is not None
#                 layover.transportation_additional = parse_result.parsed_data
#             case "TripFooter":
#                 assert isinstance(parse_result.parsed_data, raw.TripFooter)
#                 self.bid_package.pages[-1].trips[-1].footer = parse_result.parsed_data
#             case "TripSeparator":
#                 # could validate trip here
#                 pass
#             case "PageFooter":
#                 assert isinstance(parse_result.parsed_data, raw.PageFooter)
#                 # could validate page here
#                 self.bid_package.pages[-1].page_footer = parse_result.parsed_data

#     def finalize(self, ctx: dict | None = None):
#         for trip in self.bid_package.walk_trips():
#             trip.calendar_entries = collect_calendar_entries(trip)
#         if self.validator is not None:
#             self.validator.validate_bid_package(bid_package=self.bid_package, ctx=ctx)


# class DebugToFile(ParseResultToFile):
#     def result_to_txt(
#         self, parse_result: ParseResult, ctx: dict | None = None, **kwargs
#     ) -> str:
#         return f"{parse_result}"
