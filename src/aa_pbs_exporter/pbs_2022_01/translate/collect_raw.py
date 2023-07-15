from uuid import UUID, uuid5
from aa_pbs_exporter.pbs_2022_01 import PARSER_DNS
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedString,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
)
from aa_pbs_exporter.pbs_2022_01.models import raw_collected as rc


def collect_raw(parse_results: CollectedParseResults) -> rc.BidPackage:
    #         if self.source:
    #             uuid_seed = self.source.file_hash
    #         else:
    #             uuid_seed = "None"
    #         return uuid5(BIDPACKAGE_DNS, uuid_seed)
    uuid = uuid5(PARSER_DNS, repr(parse_results["kwargs"]))
    bid_package = rc.BidPackage(
        uuid=str(uuid), metadata=parse_results["kwargs"], pages=[]
    )
    for parse_result in parse_results["data"]:
        value = parse_result["parse_ident"]
        match value:
            case "PageHeader1":
                uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                page = rc.Page(uuid=str(uuid), page_header_1=parse_result, trips=[])
                bid_package["pages"].append(page)
            case "PageHeader2":
                bid_package["pages"][-1]["page_header_2"] = parse_result
            case "HeaderSeparator":
                pass
            case "BaseEquipment":
                bid_package["pages"][-1]["base_equipment"] = parse_result
            case "TripHeader":
                uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                trip = rc.Trip(
                    uuid=str(uuid),
                    header=parse_result,
                    dutyperiods=[],
                    calendar_entries=[],
                )
                bid_package["pages"][-1]["trips"].append(trip)
            case "PriorMonthDeadhead":
                uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                trip = rc.Trip(
                    uuid=str(uuid),
                    header=parse_result,
                    dutyperiods=[],
                    calendar_entries=[],
                )
                bid_package["pages"][-1]["trips"].append(trip)
            case "DutyPeriodReport":
                uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                dutyperiod = rc.DutyPeriod(
                    uuid=str(uuid), report=parse_result, flights=[]
                )
                bid_package["pages"][-1]["trips"][-1]["dutyperiods"].append(dutyperiod)
            case "Flight":
                uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                flight = rc.Flight(uuid=str(uuid), flight=parse_result)
                bid_package["pages"][-1]["trips"][-1]["dutyperiods"][-1][
                    "flights"
                ].append(flight)
            case "DutyPeriodRelease":
                bid_package["pages"][-1]["trips"][-1]["dutyperiods"][-1][
                    "release"
                ] = parse_result
            case "Layover":
                uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                layover = rc.Layover(
                    uuid=str(uuid), layover=parse_result, hotel_info=[]
                )
                bid_package["pages"][-1]["trips"][-1]["dutyperiods"][-1][
                    "layover"
                ] = layover
            case "HotelAdditional":
                bid_package["pages"][-1]["trips"][-1]["dutyperiods"][-1]["layover"][
                    "hotel_info"
                ].append(parse_result)
            case "Transportation":
                bid_package["pages"][-1]["trips"][-1]["dutyperiods"][-1]["layover"][
                    "hotel_info"
                ].append(parse_result)
            case "TransportationAdditional":
                bid_package["pages"][-1]["trips"][-1]["dutyperiods"][-1]["layover"][
                    "hotel_info"
                ].append(parse_result)
            case "CalendarOnly":
                bid_package["pages"][-1]["trips"][-1]["calendar_only"] = parse_result
            case "TripFooter":
                bid_package["pages"][-1]["trips"][-1]["footer"] = parse_result
            case "TripSeparator":
                pass
            case "PageFooter":
                bid_package["pages"][-1]["page_footer"] = parse_result
            case _:
                raise ValueError(f"{value} did not find a matching case.")
    return bid_package


def make_uuid5(self, indexed_string: IndexedString, ns_uuid: UUID = PARSER_DNS) -> UUID:
    return uuid5(ns_uuid, f"{self.idx}: {self.txt!r}")


def translate_parsed_to_raw(parse_results: CollectedParseResults) -> rc.BidPackage:
    """This is the entry point."""
    bid_package = collect_raw(parse_results=parse_results)
    return bid_package
