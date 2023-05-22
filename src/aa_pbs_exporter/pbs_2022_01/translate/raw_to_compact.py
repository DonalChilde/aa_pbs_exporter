import logging
import time
from datetime import date, datetime
from typing import Callable, Sequence, Tuple

from aa_pbs_exporter.pbs_2022_01 import messages, validate
from aa_pbs_exporter.pbs_2022_01.helpers.complete_month_day import complete_month_day
from aa_pbs_exporter.pbs_2022_01.helpers.date_range import date_range
from aa_pbs_exporter.pbs_2022_01.helpers.tz_from_iata import tz_from_iata
from aa_pbs_exporter.pbs_2022_01.models import compact, raw
from aa_pbs_exporter.snippets.datetime.parse_duration_regex import (
    parse_duration,
    pattern_HHHMM,
)
from aa_pbs_exporter.snippets.indexed_string.filters import is_numeric
from aa_pbs_exporter.snippets.indexed_string.index_and_filter_strings import (
    index_and_filter_strings,
)
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
DURATION_PATTERN = pattern_HHHMM(hm_sep=".")
TIME = "%H%M"
DATE = "%d%b%Y"
MONTH_DAY = "%m/%d"


class RawToCompact:
    def __init__(
        self,
        tz_lookup: Callable[[str], str],
        validator: validate.CompactValidator | None,
        msg_bus: Publisher | None,
    ) -> None:
        self.tz_lookup = tz_lookup
        self.compact_bid_package: compact.BidPackage | None = None
        self.validator = validator
        self.msg_bus = msg_bus

    def send_message(self, msg: MessageProtocol, ctx: dict | None):
        _ = ctx
        logger.info("%s", msg)
        if self.msg_bus is not None:
            self.msg_bus.publish_message(msg=msg)

    def translate(
        self, raw_bid_package: raw.BidPackage, ctx: dict | None = None
    ) -> compact.BidPackage:
        self.compact_bid_package = compact.BidPackage(
            uuid=raw_bid_package.uuid, source=raw_bid_package.source, pages=[]
        )
        msg = messages.StatusMessage(
            f"Translating data from raw to compact. {raw_bid_package.source}"
        )
        self.send_message(msg, ctx)
        for raw_page in raw_bid_package.pages:
            self.compact_bid_package.pages.append(
                self.translate_page(raw_page, ctx=ctx)
            )
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
        logger.debug(
            "Completed page start date %r using ref_date %r, and future date string %r",
            start,
            effective,
            raw_page.page_header_2.from_date,
        )
        end_struct = time.strptime(raw_page.page_header_2.to_date, MONTH_DAY)
        end = complete_month_day(effective, end_struct)
        logger.debug(
            "Completed page end date %r using ref_date %r, and future date string %r",
            end,
            effective,
            raw_page.page_header_2.to_date,
        )
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
        valid_dates = list(date_range(start, end))
        logger.debug("There are %s possible start dates.", len(valid_dates))
        for raw_trip in raw_page.trips:
            if "prior" in raw_trip.header.source.txt:
                # skip prior month trips
                msg = messages.StatusMessage(
                    msg=f"Skipping prior month trip {raw_trip.header.number}. "
                    f"uuid: {raw_trip.uuid}"
                )
                self.send_message(msg, ctx)
                continue
            compact_page.trips.append(
                self.translate_trip(raw_trip=raw_trip, valid_dates=valid_dates, ctx=ctx)
            )
        if self.validator is not None:
            self.validator.validate_page(
                raw_page=raw_page, compact_page=compact_page, ctx=ctx
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
        logger.debug(
            "Found %s start dates for trip %s. %r",
            len(compact_trip.start_dates),
            compact_trip.number,
            compact_trip.start_dates,
        )
        for idx, raw_dutyperiod in enumerate(raw_trip.dutyperiods, start=1):
            compact_trip.dutyperiods.append(
                self.translate_dutyperiod(idx, raw_dutyperiod, ctx=ctx)
            )
        if self.validator is not None:
            self.validator.validate_trip(
                raw_trip=raw_trip, compact_trip=compact_trip, ctx=ctx
            )
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
        for flt_idx, raw_flight in enumerate(raw_dutyperiod.flights, start=1):
            compact_dutyperiod.flights.append(
                self.translate_flight(
                    dp_idx=dp_idx, idx=flt_idx, raw_flight=raw_flight, ctx=ctx
                )
            )
        if self.validator is not None:
            self.validator.validate_dutyperiod(
                raw_dutyperiod=raw_dutyperiod,
                compact_dutyperiod=compact_dutyperiod,
                ctx=ctx,
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
        if self.validator is not None:
            self.validator.validate_flight(
                raw_flight=raw_flight, compact_flight=compact_flight, ctx=ctx
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
        if self.validator is not None:
            self.validator.validate_layover(
                raw_laypver=raw_layover, compact_layover=compact_layover, ctx=ctx
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
        if self.validator is not None:
            self.validator.validate_hotel(
                raw_hotel=raw_hotel, compact_hotel=compact_hotel, ctx=ctx
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
        if self.validator is not None:
            self.validator.validate_transportation(
                raw_transportation=raw_trans,
                compact_transportation=compact_transportation,
                ctx=ctx,
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
        if self.validator is not None:
            self.validator.check_calendar_entry_count(
                raw_trip=raw_trip, valid_dates=valid_dates, ctx=ctx
            )
        start_dates: list[date] = []
        days = self.collect_start_days(raw_trip=raw_trip)
        for day in days:
            start_date = valid_dates[day[0]]
            if self.validator is not None:
                self.validator.check_start_date(
                    day=day, start_date=start_date, raw_trip=raw_trip, ctx=ctx
                )
            start_dates.append(start_date)
        return start_dates

    def collect_start_days(self, raw_trip: raw.Trip) -> list[Tuple[int, int]]:
        indexed_days = list(
            index_and_filter_strings(
                strings=raw_trip.calendar_entries, string_filter=is_numeric
            )
        )
        return [(x.idx, int(x.txt)) for x in indexed_days]


def raw_to_compact(raw_package: raw.BidPackage, msg_bus: Publisher):
    validator = validate.CompactValidator(msg_bus=msg_bus)
    translator = RawToCompact(tz_from_iata, validator=validator, msg_bus=msg_bus)
    compact_package = translator.translate(raw_package)
    return compact_package
