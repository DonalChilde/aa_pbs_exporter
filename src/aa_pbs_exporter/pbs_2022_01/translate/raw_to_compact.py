import logging
import time
from datetime import date, datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Callable, Self, Sequence, Tuple

from aa_pbs_exporter.pbs_2022_01 import validate
from aa_pbs_exporter.pbs_2022_01.helpers.complete_month_day import complete_month_day
from aa_pbs_exporter.pbs_2022_01.helpers.date_range import date_range
from aa_pbs_exporter.pbs_2022_01.helpers.indent_level import Level
from aa_pbs_exporter.pbs_2022_01.helpers.init_publisher import indent_message
from aa_pbs_exporter.pbs_2022_01.helpers.tz_from_iata import tz_from_iata
from aa_pbs_exporter.pbs_2022_01.models import compact, raw
from aa_pbs_exporter.snippets import messages
from aa_pbs_exporter.snippets.datetime.parse_duration_regex import (
    parse_duration,
    pattern_HHHMM,
)
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.indexed_string.filters import is_numeric
from aa_pbs_exporter.snippets.indexed_string.index_and_filter_strings import (
    index_and_filter_strings,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
DURATION_PATTERN = pattern_HHHMM(hm_sep=".")
TIME = "%H%M"
DATE = "%d%b%Y"
MONTH_DAY = "%m/%d"
ERROR = "raw.translation.error"
STATUS = "raw.translation.status"
DEBUG = "raw.translation.debug"


class RawToCompact:
    def __init__(
        self,
        tz_lookup: Callable[[str], str],
        validator: validate.CompactValidator | None,
        msg_bus: messages.MessagePublisher | None,
        debug_file: Path | None = None,
    ) -> None:
        self.tz_lookup = tz_lookup
        self.compact_bid_package: compact.BidPackage | None = None
        self.validator = validator
        self.msg_bus = msg_bus
        self.debug_file = debug_file
        self.debug_fp: TextIOWrapper | None = None

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

    def send_message(self, msg: messages.Message, ctx: dict | None):
        _ = ctx
        if msg.category == STATUS:
            logger.info("\n\t%s", indent_message(msg))
        elif msg.category == DEBUG:
            logger.debug("\n\t%s", indent_message(msg))
        elif msg.category == ERROR:
            logger.warning("\n\t%s", indent_message(msg))
        if self.msg_bus is not None:
            self.msg_bus.publish_message(msg=msg)

    def translate(
        self, raw_bid_package: raw.BidPackage, ctx: dict | None = None
    ) -> compact.BidPackage:
        self.compact_bid_package = compact.BidPackage(
            uuid=raw_bid_package.uuid, source=raw_bid_package.source, pages=[]
        )
        msg = messages.Message(
            f"Translating data from raw to compact.",
            category=STATUS,
            level=Level.PKG,
        )
        self.send_message(msg, ctx)

        for page_idx, page in enumerate(raw_bid_package.pages, start=1):
            msg = messages.Message(
                f"Translating page {page.page_footer.page} {page_idx} "
                f"of {len(raw_bid_package.pages)}",
                category=DEBUG,
                level=Level.PAGE,
            )
            self.send_message(msg=msg, ctx=ctx)
            compact_page = self.translate_page(page, ctx=ctx)
            self.compact_bid_package.pages.append(compact_page)
            valid_dates = list(date_range(compact_page.start, compact_page.end))
            logger.debug("There are %s possible start dates.", len(valid_dates))
            for trip_idx, trip in enumerate(page.trips, start=1):
                msg = messages.Message(
                    f"Translating trip {trip.header.number} {trip_idx} "
                    f"of {len(page.trips)}"
                    f"uuid: {trip.uuid}",
                    category=DEBUG,
                    level=Level.TRIP,
                )
                self.send_message(msg=msg, ctx=ctx)
                if "prior" in trip.header.source.txt:
                    # skip prior month trips
                    # msg = messages.Message(
                    #     f"Skipping prior month trip {trip.header.number}. "
                    #     f"uuid: {trip.uuid}",
                    #     category=STATUS,
                    #     level=Level.TRIP + 1,
                    # )
                    # self.send_message(msg, ctx)
                    continue
                compact_trip = self.translate_trip(trip, valid_dates, ctx=ctx)
                compact_page.trips.append(compact_trip)
                for dp_idx, dutyperiod in enumerate(trip.dutyperiods, start=1):
                    msg = messages.Message(
                        f"Translating dutyperiod {dp_idx} "
                        f"of {len(trip.dutyperiods)}"
                        f"uuid: {dutyperiod.uuid}",
                        category=DEBUG,
                        level=Level.DP,
                    )
                    self.send_message(msg=msg, ctx=ctx)
                    compact_dutyperiod = self.translate_dutyperiod(
                        dp_idx, dutyperiod, ctx=ctx
                    )
                    compact_trip.dutyperiods.append(compact_dutyperiod)
                    for flt_idx, flight in enumerate(dutyperiod.flights, start=1):
                        msg = messages.Message(
                            f"Translating flight {flight.flight_number} {flt_idx} "
                            f"of {len(dutyperiod.flights)}"
                            f"uuid: {flight.source.uuid5()}",
                            category=DEBUG,
                            level=Level.FLT,
                        )
                        self.send_message(msg=msg, ctx=ctx)
                        compact_flight = self.translate_flight(
                            dp_idx, flt_idx, flight, ctx=ctx
                        )
                        compact_dutyperiod.flights.append(compact_flight)

        if self.validator is not None:
            self.validator.validate(
                raw_bid=raw_bid_package, compact_bid=self.compact_bid_package, ctx=ctx
            )
        return self.compact_bid_package

    def translate_page(
        self, raw_page: raw.Page, ctx: dict | None = None
    ) -> compact.Page:
        assert raw_page.page_footer is not None
        assert raw_page.page_header_2 is not None

        effective = datetime.strptime(raw_page.page_footer.effective, DATE).date()
        start_struct = time.strptime(raw_page.page_header_2.from_date, MONTH_DAY)
        start = complete_month_day(effective, start_struct)
        msg = messages.Message(
            f"Completed page start date {start} using ref_date {effective}, and "
            f"future date string {raw_page.page_header_2.from_date}",
            category=DEBUG,
            level=Level.PAGE + 1,
        )
        self.send_message(msg=msg, ctx=ctx)
        end_struct = time.strptime(raw_page.page_header_2.to_date, MONTH_DAY)
        end = complete_month_day(effective, end_struct)
        msg = messages.Message(
            f"Completed page end date {end} using ref_date {effective}, and "
            f"future date string {raw_page.page_header_2.to_date}",
            category=DEBUG,
            level=Level.PAGE + 1,
        )
        self.send_message(msg=msg, ctx=ctx)
        trips: list[compact.Trip] = []
        compact_page = compact.Page(
            uuid=raw_page.uuid,
            base=raw_page.page_footer.base,
            satellite_base=raw_page.page_footer.satelite_base,
            equipment=raw_page.page_footer.equipment,
            division=raw_page.page_footer.division,
            issued=datetime.strptime(raw_page.page_footer.issued, DATE),
            effective=effective,
            start=start,
            end=end,
            trips=trips,
            number=raw_page.page_footer.page,
        )
        return compact_page

    def translate_trip(
        self,
        raw_trip: raw.Trip,
        valid_dates: Sequence[date],
        ctx: dict | None = None,
    ) -> compact.Trip:
        dutyperiods: list[compact.DutyPeriod] = []
        assert raw_trip.footer is not None
        compact_trip = compact.Trip(
            uuid=raw_trip.uuid,
            number=raw_trip.header.number,
            positions=raw_trip.header.positions.split(),
            operations=raw_trip.header.operations,
            qualifications=raw_trip.header.qualifications,
            block=parse_duration(
                DURATION_PATTERN, raw_trip.footer.block
            ).to_timedelta(),
            synth=parse_duration(
                DURATION_PATTERN, raw_trip.footer.synth
            ).to_timedelta(),
            total_pay=parse_duration(
                DURATION_PATTERN, raw_trip.footer.total_pay
            ).to_timedelta(),
            tafb=parse_duration(DURATION_PATTERN, raw_trip.footer.tafb).to_timedelta(),
            dutyperiods=dutyperiods,
            start_dates=[],
        )
        compact_trip.start_dates = self.collect_start_dates(
            valid_dates=valid_dates, raw_trip=raw_trip, ctx=ctx
        )
        msg = messages.Message(
            f"Found {len(compact_trip.start_dates)} start dates for "
            f"trip {compact_trip.number}. {compact_trip.start_dates!r}",
            category=DEBUG,
            level=Level.TRIP + 1,
        )
        self.send_message(msg=msg, ctx=ctx)
        return compact_trip

    def translate_dutyperiod(
        self, dp_idx: int, raw_dutyperiod: raw.DutyPeriod, ctx: dict | None = None
    ) -> compact.DutyPeriod:
        assert raw_dutyperiod.release is not None
        report_station = raw_dutyperiod.flights[0].departure_station
        release_station: str = raw_dutyperiod.flights[-1].arrival_station
        report = self.split_times(raw_dutyperiod.report.report, report_station)
        release = self.split_times(raw_dutyperiod.release.release, release_station)
        flights: list[compact.Flight] = []
        compact_dutyperiod = compact.DutyPeriod(
            uuid=raw_dutyperiod.uuid,
            idx=dp_idx,
            report=report,
            report_station=report_station,
            release=release,
            release_station=release_station,
            block=parse_duration(
                DURATION_PATTERN, raw_dutyperiod.release.block
            ).to_timedelta(),
            synth=parse_duration(
                DURATION_PATTERN, raw_dutyperiod.release.synth
            ).to_timedelta(),
            total_pay=parse_duration(
                DURATION_PATTERN, raw_dutyperiod.release.total_pay
            ).to_timedelta(),
            duty=parse_duration(
                DURATION_PATTERN, raw_dutyperiod.release.duty
            ).to_timedelta(),
            flight_duty=parse_duration(
                DURATION_PATTERN, raw_dutyperiod.release.flight_duty
            ).to_timedelta(),
            layover=self.translate_layover(raw_dutyperiod.layover, ctx=ctx),
            flights=flights,
        )
        return compact_dutyperiod

    def translate_flight(
        self, dp_idx: int, idx: int, raw_flight: raw.Flight, ctx: dict | None = None
    ) -> compact.Flight:
        departure_station = raw_flight.departure_station
        arrival_station = raw_flight.arrival_station
        departure = self.split_times(raw_flight.departure_time, departure_station)
        arrival = self.split_times(raw_flight.arrival_time, arrival_station)
        compact_flight = compact.Flight(
            uuid=raw_flight.uuid5(),
            dp_idx=dp_idx,
            idx=idx,
            dep_arr_day=raw_flight.dep_arr_day,
            eq_code=raw_flight.eq_code,
            number=raw_flight.flight_number,
            deadhead=bool(raw_flight.deadhead),
            departure_station=departure_station,
            departure=departure,
            meal=raw_flight.meal,
            arrival_station=arrival_station,
            arrival=arrival,
            block=parse_duration(DURATION_PATTERN, raw_flight.block).to_timedelta(),
            synth=parse_duration(DURATION_PATTERN, raw_flight.synth).to_timedelta(),
            ground=parse_duration(DURATION_PATTERN, raw_flight.ground).to_timedelta(),
            equipment_change=bool(raw_flight.equipment_change),
        )
        return compact_flight

    def translate_layover(
        self, raw_layover: raw.Layover | None, ctx: dict | None = None
    ) -> compact.Layover | None:
        if raw_layover is None:
            return None
        compact_layover = compact.Layover(
            uuid=raw_layover.uuid,
            odl=parse_duration(DURATION_PATTERN, raw_layover.rest).to_timedelta(),
            city=raw_layover.layover_city,
            hotel_info=self.translate_hotel_info(
                raw_hotel_info=raw_layover.hotel_info, ctx=ctx
            ),
        )
        return compact_layover

    def translate_hotel_info(
        self, raw_hotel_info: Sequence[raw.HotelInfo], ctx: dict | None
    ) -> list[compact.HotelInfo]:
        _ = ctx
        compact_hotel_infos: list[compact.HotelInfo] = []
        for info in raw_hotel_info:
            compact_hotel = self.translate_hotel(info.hotel)
            compact_transportation = self.translate_transportation(info.transportation)
            compact_hotel_info = compact.HotelInfo(
                hotel=compact_hotel, transportation=compact_transportation
            )
            compact_hotel_infos.append(compact_hotel_info)
        return compact_hotel_infos

    def translate_hotel(
        self, raw_hotel: raw.Hotel | raw.HotelAdditional | None, ctx: dict | None = None
    ) -> compact.Hotel | None:
        if raw_hotel is None:
            return None
        compact_hotel = compact.Hotel(
            uuid=raw_hotel.uuid5(), name=raw_hotel.name, phone=raw_hotel.phone
        )
        return compact_hotel

    def translate_transportation(
        self,
        raw_trans: raw.Transportation | raw.TransportationAdditional | None,
        ctx: dict | None = None,
    ) -> compact.Transportation | None:
        if raw_trans is None:
            return None
        compact_transportation = compact.Transportation(
            uuid=raw_trans.uuid5(), name=raw_trans.name, phone=raw_trans.phone
        )
        return compact_transportation

    def split_times(self, lclhbt: str, iata: str) -> compact.LclHbt:
        lcl_str, hbt_str = lclhbt.split("/")
        tz_str = self.tz_lookup(iata)
        local_time = datetime.strptime(lcl_str, TIME).time()
        hbt_time = datetime.strptime(hbt_str, TIME).time()
        return compact.LclHbt(lcl=local_time, hbt=hbt_time, tz_name=tz_str)

    def collect_start_dates(
        self, valid_dates: Sequence[date], raw_trip: raw.Trip, ctx: dict | None
    ) -> list[date]:
        if not len(raw_trip.calendar_entries) == len(valid_dates):
            msg = messages.Message(
                f"Count of calendar_entries: {len(raw_trip.calendar_entries)} "
                f"does not match valid_dates: {len(valid_dates)}. "
                f"uuid: {raw_trip.uuid}",
                category=ERROR,
                level=Level.TRIP + 1,
            )
            self.send_message(msg=msg, ctx=ctx)
        start_dates: list[date] = []
        days = self.collect_start_days(raw_trip=raw_trip)
        for day in days:
            start_date = valid_dates[day[0]]
            if day[1] != start_date.day:
                msg = messages.Message(
                    f"Partial date: {day!r} does not match day of date: "
                    f"{start_date.isoformat()}. "
                    f"uuid:{raw_trip.uuid}",
                    category=ERROR,
                    level=Level.TRIP + 1,
                )
                self.send_message(msg=msg, ctx=ctx)
            start_dates.append(start_date)
        return start_dates

    def collect_start_days(self, raw_trip: raw.Trip) -> list[Tuple[int, int]]:
        indexed_days = list(
            index_and_filter_strings(
                strings=raw_trip.calendar_entries, string_filter=is_numeric
            )
        )
        return [(x.idx, int(x.txt)) for x in indexed_days]


def raw_to_compact(
    raw_package: raw.BidPackage,
    msg_bus: messages.MessagePublisher | None,
    debug_file: Path | None = None,
):
    validator = validate.CompactValidator(msg_bus=msg_bus)
    with RawToCompact(
        tz_lookup=tz_from_iata, validator=validator, msg_bus=None, debug_file=debug_file
    ) as translator:
        compact_package = translator.translate(raw_package)
    return compact_package
