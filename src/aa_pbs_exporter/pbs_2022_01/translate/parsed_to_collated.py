import logging
from io import TextIOWrapper
from pathlib import Path
import traceback
from typing import Self

from aa_pbs_exporter.pbs_2022_01.models import compact
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.string.indent import indent
from uuid import UUID, uuid5

from aa_pbs_exporter.pbs_2022_01 import PARSER_DNS
from aa_pbs_exporter.pbs_2022_01.models import collated
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ParsedToCollated:
    def __init__(
        self,
        debug_file: Path | None = None,
    ) -> None:
        self.debug_file = debug_file
        self.debug_fp: TextIOWrapper | None = None

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="a", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug_fp is not None:
            self.debug_fp.close()

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def translate(self, parse_results: CollectedParseResults) -> collated.BidPackage:
        try:
            return self._translate(parse_results=parse_results)
        except Exception as error:
            logger.exception("Unexpected error during translation.")
            self.debug_write("".join(traceback.format_exception(error)), 0)
            raise error

    def _translate(self, parse_results: CollectedParseResults) -> collated.BidPackage:
        uuid = uuid5(PARSER_DNS, repr(parse_results["metadata"]))
        bid_package = collated.BidPackage(
            uuid=str(uuid), metadata=parse_results["metadata"], pages=[]
        )
        for parse_result in parse_results["data"]:
            value = parse_result["parse_ident"]
            match value:
                case "PageHeader1":
                    uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                    page = collated.Page(
                        uuid=str(uuid), page_header_1=parse_result, trips=[]
                    )
                    bid_package["pages"].append(page)
                case "PageHeader2":
                    bid_package["pages"][-1]["page_header_2"] = parse_result
                case "HeaderSeparator":
                    pass
                case "BaseEquipment":
                    bid_package["pages"][-1]["base_equipment"] = parse_result
                case "TripHeader":
                    uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                    trip = collated.Trip(
                        uuid=str(uuid),
                        header=parse_result,
                        dutyperiods=[],
                        calendar_entries=[],
                    )
                    bid_package["pages"][-1]["trips"].append(trip)
                case "PriorMonthDeadhead":
                    uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                    trip = collated.Trip(
                        uuid=str(uuid),
                        header=parse_result,
                        dutyperiods=[],
                        calendar_entries=[],
                    )
                    bid_package["pages"][-1]["trips"].append(trip)
                case "DutyPeriodReport":
                    uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                    dutyperiod = collated.DutyPeriod(
                        uuid=str(uuid), report=parse_result, flights=[]
                    )
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["dutyperiods"].append(dutyperiod)

                case "Flight":
                    uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                    flight = collated.Flight(uuid=str(uuid), flight=parse_result)
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["dutyperiods"][-1]["flights"].append(flight)
                case "DutyPeriodRelease":
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["dutyperiods"][-1]["release"] = parse_result
                case "Layover":
                    uuid = uuid5(PARSER_DNS, repr(parse_result["source"]))
                    layover = collated.Layover(
                        uuid=str(uuid), layover=parse_result, hotel_info=[]
                    )
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["dutyperiods"][-1]["layover"] = layover
                case "HotelAdditional":
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["dutyperiods"][-1]["layover"]["hotel_info"].append(
                        parse_result
                    )
                case "Transportation":
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["dutyperiods"][-1]["layover"]["hotel_info"].append(
                        parse_result
                    )
                case "TransportationAdditional":
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["dutyperiods"][-1]["layover"]["hotel_info"].append(
                        parse_result
                    )
                case "CalendarOnly":
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["calendar_only"] = parse_result
                case "TripFooter":
                    trip = bid_package["pages"][-1]["trips"][-1]
                    trip["calendar_entries"].extend(
                        parse_result["parsed_data"]["calendar"]
                    )
                    trip["footer"] = parse_result
                case "TripSeparator":
                    pass
                case "PageFooter":
                    bid_package["pages"][-1]["page_footer"] = parse_result
                case _:
                    raise ValueError(f"{value} did not find a matching case.")
        return bid_package


def translate_parsed_to_collated(
    parse_results: CollectedParseResults, debug_file: Path | None
) -> collated.BidPackage:
    with ParsedToCollated(debug_file=debug_file) as translator:
        collated_bid_package = translator.translate(parse_results=parse_results)
    return collated_bid_package
