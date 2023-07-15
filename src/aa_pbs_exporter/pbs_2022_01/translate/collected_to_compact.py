import logging
import time
from datetime import date, datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Callable, Self, Sequence, Tuple, cast
from uuid import UUID, uuid5

from aa_pbs_exporter.pbs_2022_01 import PARSER_DNS, validate
from aa_pbs_exporter.pbs_2022_01.helpers import elapsed
from aa_pbs_exporter.pbs_2022_01.helpers.complete_month_day import complete_month_day
from aa_pbs_exporter.pbs_2022_01.helpers.date_range import date_range
from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
from aa_pbs_exporter.pbs_2022_01.helpers.tz_from_iata import tz_from_iata
from aa_pbs_exporter.pbs_2022_01.models import compact, common
from aa_pbs_exporter.pbs_2022_01.models import raw_td as raw
from aa_pbs_exporter.pbs_2022_01.models import raw_collected as collected
from aa_pbs_exporter.pbs_2022_01.helpers import instant_time as instant
from aa_pbs_exporter.snippets.datetime.parse_duration_regex import (
    parse_duration,
    pattern_HHHMM,
)
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.hash.file_hash import HashedFileDict
from aa_pbs_exporter.snippets.indexed_string.filters import is_numeric
from aa_pbs_exporter.snippets.indexed_string.index_and_filter_strings import (
    index_and_filter_strings,
)
from aa_pbs_exporter.snippets.string.indent import indent

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
DURATION_PATTERN = pattern_HHHMM(hm_sep=".")
TIME = "%H%M"
DATE = "%d%b%Y"
MONTH_DAY = "%m/%d"
ERROR = "raw.translation.error"
STATUS = "raw.translation.status"
DEBUG = "raw.translation.debug"


class CollectedToCompact:
    def __init__(
        self,
        tz_lookup: Callable[[str], str],
        validator: validate.ValidateCompact | None,
        debug_file: Path | None = None,
    ) -> None:
        self.tz_lookup = tz_lookup
        self.compact_bid_package: compact.BidPackage | None = None
        self.validator = validator
        self.debug_file = debug_file
        self.debug_fp: TextIOWrapper | None = None
        self.hbt_tz_name: str = ""

    def __enter__(self) -> Self:
        if self.debug_file is not None:
            validate_file_out(self.debug_file, overwrite=True)
            self.debug_fp = open(self.debug_file, mode="w", encoding="utf-8")
            if self.validator is not None:
                self.validator.debug_fp = self.debug_fp
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.debug_fp is not None:
            self.debug_fp.close()

    def debug_write(self, value: str, indent_level: int = 0):
        if self.debug_fp is not None:
            print(indent(value, indent_level), file=self.debug_fp)

    def translate_source(self, raw_source: dict[str, str]) -> common.HashedFile:
        source = cast(HashedFileDict, raw_source)
        return common.HashedFile(**source)

    def translate(
        self, collected_bid_package: collected.BidPackage
    ) -> compact.BidPackage:
        start = time.perf_counter_ns()
        self.debug_write(
            f"********** Translating from collected to compact. uuid:{collected_bid_package['uuid']} **********",
            Level.PKG,
        )
        first_page = collected_bid_package["pages"][0]
        page_footer = cast(raw.PageFooter, first_page["page_footer"]["parsed_data"])
        self.hbt_tz_name = self.tz_lookup(page_footer["base"])
        raw_source: dict[str, str] | None = collected_bid_package["metadata"].get(
            "source", None
        )
        if raw_source is None:
            source: common.HashedFile | None = None
        else:
            source = self.translate_source(raw_source)
        compact_bid = compact.BidPackage(
            uuid=UUID(collected_bid_package["uuid"]), source=source, pages=[]
        )
        for page_idx, raw_page in enumerate(collected_bid_package["pages"], start=1):
            self.debug_write(
                f"Translating page {raw_page['page_footer']['parsed_data']['page']} "
                f"{page_idx} of {len(collected_bid_package['pages'])}",
                Level.PAGE,
            )
            compact_page = self.translate_page(collected_page=raw_page)
            compact_bid.pages.append(compact_page)

        end = time.perf_counter_ns()
        self.debug_write(
            f"Translation complete in {elapsed.nanos_to_seconds(start,end):4f} seconds."
        )
        return compact_bid

    def translate_page(self, collected_page: collected.Page) -> compact.Page:
        page_header_2 = cast(
            raw.PageHeader2, collected_page["page_header_2"]["parsed_data"]
        )
        page_footer = cast(raw.PageFooter, collected_page["page_footer"]["parsed_data"])
        effective = datetime.strptime(page_footer["effective"], DATE).date()
        start_struct = time.strptime(page_header_2["from_date"], MONTH_DAY)
        start = complete_month_day(effective, start_struct)

        self.debug_write(
            f"Completed page start date {start} using ref_date {effective}, and "
            f"future date string {page_header_2['from_date']}",
            Level.PAGE + 1,
        )
        end_struct = time.strptime(page_header_2["to_date"], MONTH_DAY)
        end = complete_month_day(effective, end_struct)
        self.debug_write(
            f"Completed page end date {end} using ref_date {effective}, and "
            f"future date string {page_header_2['to_date']}",
            Level.PAGE + 1,
        )
        valid_dates = list(date_range(start, end))
        trips = self.translate_trips(collected_page["trips"], valid_dates=valid_dates)
        compact_page = compact.Page(
            uuid=UUID(collected_page["uuid"]),
            base=page_footer["base"],
            satellite_base=page_footer["satelite_base"],
            equipment=page_footer["equipment"],
            division=page_footer["division"],
            issued=datetime.strptime(page_footer["issued"], DATE),
            effective=effective,
            start=start,
            end=end,
            trips=trips,
            number=page_footer["page"],
        )
        return compact_page

    def translate_trips(
        self, collected_trips: Sequence[collected.Trip], valid_dates: Sequence[date]
    ) -> list[compact.Trip]:
        trips: list[compact.Trip] = []
        for trip_idx, trip in enumerate(collected_trips, start=1):
            trip_number = trip["header"]["parsed_data"]["number"]
            self.debug_write(
                f"Translating trip {trip_number} "
                f"{trip_idx} of {len(collected_trips)}"
                f"uuid: {trip['uuid']}",
                Level.TRIP,
            )
            if "prior" in trip["header"]["source"]["txt"]:
                # skip prior month trips
                self.debug_write(
                    f"Skipping prior month trip: {trip_number}", Level.TRIP
                )
                continue
            trips.append(
                self.translate_trip(collected_trip=trip, valid_dates=valid_dates)
            )
        return trips

    def translate_trip(
        self,
        collected_trip: collected.Trip,
        valid_dates: Sequence[date],
    ) -> compact.Trip:
        footer = cast(raw.TripFooter, collected_trip["footer"]["parsed_data"])
        header = cast(raw.TripHeader, collected_trip["header"]["parsed_data"])
        dutyperiods = self.translate_dutyperiods(collected_trip["dutyperiods"])
        start_dates = self.collect_start_dates(
            valid_dates=valid_dates, collected_trip=collected_trip
        )
        compact_trip = compact.Trip(
            uuid=UUID(collected_trip["uuid"]),
            number=header["number"],
            positions=header["positions"].split(),
            operations=header["operations"],
            qualifications=header["qualifications"],
            block=parse_duration(DURATION_PATTERN, footer["block"]).to_timedelta(),
            synth=parse_duration(DURATION_PATTERN, footer["synth"]).to_timedelta(),
            total_pay=parse_duration(
                DURATION_PATTERN, footer["total_pay"]
            ).to_timedelta(),
            tafb=parse_duration(DURATION_PATTERN, footer["tafb"]).to_timedelta(),
            dutyperiods=dutyperiods,
            start_dates=start_dates,
        )
        return compact_trip

    def translate_dutyperiods(
        self,
        collected_dutyperiods: Sequence[collected.DutyPeriod],
    ) -> list[compact.DutyPeriod]:
        compact_dutyperiods: list[compact.DutyPeriod] = []
        for dp_idx, dutyperiod in enumerate(collected_dutyperiods, start=1):
            self.debug_write(
                f"Translating dutyperiod {dp_idx} of {len(collected_dutyperiods)} "
                f"uuid: {dutyperiod['uuid']}",
                Level.DP,
            )
            compact_dutyperiod = self.translate_dutyperiod(
                collected_dutyperiod=dutyperiod, dp_idx=dp_idx
            )
            compact_dutyperiods.append(compact_dutyperiod)
        return compact_dutyperiods

    def translate_dutyperiod(
        self,
        collected_dutyperiod: collected.DutyPeriod,
        dp_idx: int,
    ) -> compact.DutyPeriod:
        report = cast(
            raw.DutyPeriodReport, collected_dutyperiod["report"]["parsed_data"]
        )
        release = cast(
            raw.DutyPeriodRelease, collected_dutyperiod["release"]["parsed_data"]
        )

        first_flight = cast(
            raw.Flight, collected_dutyperiod["flights"][0]["flight"]["parsed_data"]
        )
        last_flight = cast(
            raw.Flight, collected_dutyperiod["flights"][-1]["flight"]["parsed_data"]
        )
        report_station = first_flight["departure_station"]
        release_station = last_flight["arrival_station"]
        report_time = self.split_times(
            report["report"], report_station, self.hbt_tz_name
        )
        release_time = self.split_times(
            release["release"], release_station, self.hbt_tz_name
        )
        flights = self.translate_flights(collected_dutyperiod["flights"], dp_idx)
        raw_layover = collected_dutyperiod.get("layover", None)
        if raw_layover is None:
            layover = None
        else:
            layover = self.translate_layover(raw_layover)
        compact_dutyperiod = compact.DutyPeriod(
            uuid=UUID(collected_dutyperiod["uuid"]),
            idx=dp_idx,
            report=report_time,
            report_station=report_station,
            release=release_time,
            release_station=release_station,
            block=parse_duration(DURATION_PATTERN, release["block"]).to_timedelta(),
            synth=parse_duration(DURATION_PATTERN, release["synth"]).to_timedelta(),
            total_pay=parse_duration(
                DURATION_PATTERN, release["total_pay"]
            ).to_timedelta(),
            duty=parse_duration(DURATION_PATTERN, release["duty"]).to_timedelta(),
            flight_duty=parse_duration(
                DURATION_PATTERN, release["flight_duty"]
            ).to_timedelta(),
            layover=layover,
            flights=flights,
        )
        return compact_dutyperiod

    def translate_flights(
        self, collected_flights: list[collected.Flight], dp_idx: int
    ) -> list[compact.Flight]:
        compact_flights: list[compact.Flight] = []
        for flt_idx, collected_flight in enumerate(collected_flights, start=1):
            self.debug_write(
                f"Translating flight {collected_flight['flight']['parsed_data']['flight_number']} "
                f"{flt_idx} of {len(collected_flights)}"
                f"uuid: {collected_flight['uuid']}",
                Level.FLT,
            )
            compact_flight = self.translate_flight(collected_flight, dp_idx, flt_idx)
            compact_flights.append(compact_flight)
        return compact_flights

    def translate_flight(
        self,
        collected_flight: collected.Flight,
        dp_idx: int,
        idx: int,
    ) -> compact.Flight:
        flight = cast(raw.Flight, collected_flight["flight"]["parsed_data"])
        departure_station = flight["departure_station"]
        arrival_station = flight["arrival_station"]
        departure = self.split_times(
            flight["departure_time"], departure_station, self.hbt_tz_name
        )
        arrival = self.split_times(
            flight["arrival_time"], arrival_station, self.hbt_tz_name
        )
        compact_flight = compact.Flight(
            uuid=UUID(collected_flight["uuid"]),
            dp_idx=dp_idx,
            idx=idx,
            dep_arr_day=flight["dep_arr_day"],
            eq_code=flight["eq_code"],
            number=flight["flight_number"],
            deadhead=bool(flight["deadhead"]),
            departure_station=departure_station,
            departure=departure,
            meal=flight["meal"],
            arrival_station=arrival_station,
            arrival=arrival,
            block=parse_duration(DURATION_PATTERN, flight["block"]).to_timedelta(),
            synth=parse_duration(DURATION_PATTERN, flight["synth"]).to_timedelta(),
            ground=parse_duration(DURATION_PATTERN, flight["ground"]).to_timedelta(),
            equipment_change=bool(flight["equipment_change"]),
        )
        return compact_flight

    def translate_layover(
        self, collected_layover: collected.Layover
    ) -> compact.Layover:
        layover = cast(raw.Layover, collected_layover["layover"]["parsed_data"])
        compact_layover = compact.Layover(
            uuid=UUID(collected_layover["uuid"]),
            odl=parse_duration(DURATION_PATTERN, layover["rest"]).to_timedelta(),
            city=layover["layover_city"],
            hotel_info=self.translate_hotel_info(collected_layover=collected_layover),
        )
        return compact_layover

    def translate_hotel_info(
        self, collected_layover: collected.Layover
    ) -> list[compact.HotelInfo]:
        layover = cast(raw.Layover, collected_layover["layover"]["parsed_data"])
        uuid = uuid5(PARSER_DNS, collected_layover["uuid"])
        hotel = compact.Hotel(
            uuid=uuid,
            name=layover["name"],
            phone=layover["phone"],
        )
        hotel_infos: list[compact.HotelInfo] = []
        hotel_infos.append(compact.HotelInfo(hotel=hotel, transportation=[]))
        for result in collected_layover["hotel_info"]:
            uuid = uuid5(PARSER_DNS, repr(result["source"]))
            if result["parse_ident"] == "Transportation":
                data = cast(raw.Transportation, result["parsed_data"])
                transportation = compact.Transportation(
                    uuid=uuid, name=data["name"], phone=data["phone"]
                )
                hotel_infos[-1].transportation.append(transportation)
            if result["parse_ident"] == "TransportationAdditional":
                data = cast(raw.TransportationAdditional, result["parsed_data"])
                transportation = compact.Transportation(
                    uuid=uuid, name=data["name"], phone=data["phone"]
                )
                hotel_infos[-1].transportation.append(transportation)
            if result["parse_ident"] == "HotelAdditional":
                data = cast(raw.HotelAdditional, result["parsed_data"])
                hotel = compact.Hotel(uuid=uuid, name=data["name"], phone=data["phone"])
                hotel_infos.append(compact.HotelInfo(hotel=hotel, transportation=[]))
        return hotel_infos

    def split_times(
        self, lclhbt: str, lcl_iata: str, hbt_tz_name: str
    ) -> compact.LclHbt:
        lcl_str, hbt_str = lclhbt.split("/")
        lcl_tz_name = self.tz_lookup(lcl_iata)
        local_time = datetime.strptime(lcl_str, TIME).time()
        hbt_time = datetime.strptime(hbt_str, TIME).time()
        local_instant = instant.InstantTime(time=local_time, tz_name=lcl_tz_name)
        hbt_instant = instant.InstantTime(time=hbt_time, tz_name=hbt_tz_name)
        return compact.LclHbt(lcl=local_instant, hbt=hbt_instant)

    # def split_times(self, lclhbt: str, iata: str) -> compact.LclHbt:
    #     lcl_str, hbt_str = lclhbt.split("/")
    #     tz_str = self.tz_lookup(iata)
    #     local_time = datetime.strptime(lcl_str, TIME).time()
    #     hbt_time = datetime.strptime(hbt_str, TIME).time()
    #     return compact.LclHbt(lcl=local_time, hbt=hbt_time, tz_name=tz_str)

    def collect_start_dates(
        self,
        valid_dates: Sequence[date],
        collected_trip: collected.Trip,
    ) -> list[date]:
        # TODO consider moving the collection of calendar entries here?
        if not len(collected_trip["calendar_entries"]) == len(valid_dates):
            self.debug_write(
                f"Count of calendar_entries: {len(collected_trip['calendar_entries'])} "
                f"does not match valid_dates: {len(valid_dates)}. "
                f"uuid: {collected_trip['uuid']}",
                Level.TRIP + 1,
            )
        start_dates: list[date] = []
        days = self.collect_start_days(collected_trip=collected_trip)
        for day in days:
            start_date = valid_dates[day[0]]
            if day[1] != start_date.day:
                self.debug_write(
                    f"Partial date: {day!r} does not match day of date: "
                    f"{start_date.isoformat()}. "
                    f"uuid:{collected_trip['uuid']}",
                    Level.TRIP + 1,
                )
            start_dates.append(start_date)
        return start_dates

    def collect_start_days(
        self, collected_trip: collected.Trip
    ) -> list[Tuple[int, int]]:
        indexed_days = list(
            index_and_filter_strings(
                strings=collected_trip["calendar_entries"], string_filter=is_numeric
            )
        )
        return [(x.idx, int(x.txt)) for x in indexed_days]


def translate_collected_to_compact(
    collected_bid_package: collected.BidPackage, debug_file: Path
) -> compact.BidPackage:
    validator = None
    with CollectedToCompact(
        tz_lookup=tz_from_iata, validator=validator, debug_file=debug_file
    ) as translator:
        compact_bid_package = translator.translate(
            collected_bid_package=collected_bid_package
        )
    return compact_bid_package


# TODO separate validator, use uuid to match objects.
