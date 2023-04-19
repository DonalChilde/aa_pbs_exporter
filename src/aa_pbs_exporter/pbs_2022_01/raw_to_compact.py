from datetime import date, datetime,  timedelta
from typing import Callable
import time

from aa_pbs_exporter.pbs_2022_01.models import compact, raw
from aa_pbs_exporter.snippets.datetime.parse_duration_regex import (
    parse_duration,
    pattern_HHHMMSSFS,
)
from aa_pbs_exporter.snippets.indexed_string.filters import is_numeric
from aa_pbs_exporter.snippets.indexed_string.index_and_filter_strings import (
    index_and_filter_strings,
)

DURATION_PATTERN = pattern_HHHMMSSFS(hm_sep=".")
TIME = "%H%M"
DATE = "%d%b%Y"
MONTH_DAY = "%m/%d"


class Translator:
    def __init__(self, tz_lookup: Callable[[str], str]) -> None:
        self.tz_lookup = tz_lookup
        self.compact_bid_package = None

    def translate(self, raw_bid_package: raw.BidPackage) -> compact.BidPackage:
        self.compact_bid_package = compact.BidPackage(
            source=raw_bid_package.source, pages=[]
        )
        for raw_page in raw_bid_package.pages:
            self.compact_bid_package.pages.append(self.translate_page(raw_page))
        return self.compact_bid_package

    def translate_page(self, raw_page: raw.Page) -> compact.Page:
        assert raw_page.page_footer is not None
        assert raw_page.page_header_2 is not None
        effective = datetime.strptime(raw_page.page_footer.effective, DATE).date()
        start = complete_future_date(
            ref_date=effective, future=raw_page.page_header_2.from_date, strf=MONTH_DAY
        )
        end = complete_future_date(
            ref_date=effective, future=raw_page.page_header_2.to_date, strf=MONTH_DAY
        )
        trips = []
        compact_page = compact.Page(
            base=raw_page.page_footer.base,
            satellite_base=raw_page.page_footer.satelite_base,
            equipment=raw_page.page_footer.equipment,
            division=raw_page.page_footer.division,
            issued=datetime.strptime(raw_page.page_footer.issued, DATE),
            effective=effective,
            start=start,
            end=end,
            trips=trips,
        )
        for raw_trip in  raw_page.trips:
            if "prior" in raw_trip.header.source.txt:
                # skip prior month trips
                continue
            compact_page.trips.append(
                self.translate_trip(raw_trip=raw_trip, from_date=start, to_date=end)
            )
        return compact_page

    def translate_trip(
        self, raw_trip: raw.Trip, from_date: date, to_date: date
    ) -> compact.Trip:
        dutyperiods = []
        start_dates = []
        assert raw_trip.footer is not None
        compact_trip = compact.Trip(
            number=raw_trip.header.number,
            positions=raw_trip.header.positions.split(),
            operations=raw_trip.header.operations,
            special_qualifications=bool(raw_trip.header.special_qualification),
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
            start_dates=start_dates,
        )
        calendar_entries = collect_calendar_entries(raw_trip)
        starts = get_start_dates(
            from_date=from_date, to_date=to_date, calendar_entries=calendar_entries
        )
        compact_trip.start_dates.extend(starts)
        for idx, raw_dutyperiod in enumerate(raw_trip.dutyperiods, start=1):
            compact_trip.dutyperiods.append(
                self.translate_dutyperiod(idx, raw_dutyperiod)
            )
        return compact_trip

    def translate_dutyperiod(
        self, idx: int, raw_dutyperiod: raw.DutyPeriod
    ) -> compact.DutyPeriod:
        assert raw_dutyperiod.release is not None
        report_station = raw_dutyperiod.flights[0].departure_station
        release_station: str = raw_dutyperiod.flights[-1].arrival_station
        report = self.split_times(raw_dutyperiod.report.report, report_station)
        release = self.split_times(raw_dutyperiod.release.release, release_station)
        flights = []
        compact_dutyperiod = compact.DutyPeriod(
            idx=idx,
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
            layover=self.translate_layover(raw_dutyperiod.layover),
            flights=flights,
        )
        for flt_idx, raw_flight in enumerate(raw_dutyperiod.flights, start=1):
            compact_dutyperiod.flights.append(
                self.translate_flight(flt_idx, raw_flight)
            )
        return compact_dutyperiod

    def translate_flight(self, idx: int, raw_flight: raw.Flight) -> compact.Flight:
        departure_station = raw_flight.departure_station
        arrival_station = raw_flight.arrival_station
        departure = self.split_times(raw_flight.departure_time, departure_station)
        arrival = self.split_times(raw_flight.arrival_time, arrival_station)
        compact_flight = compact.Flight(
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
        self, raw_layover: raw.Layover | None
    ) -> compact.Layover | None:
        if raw_layover is None:
            return None
        compact_layover = compact.Layover(
            odl=parse_duration(DURATION_PATTERN, raw_layover.hotel.rest).to_timedelta(),
            city=raw_layover.hotel.layover_city,
            hotel=self.translate_hotel(raw_layover.hotel),
            transportation=self.translate_transportation(raw_layover.transportation),
            hotel_additional=self.translate_hotel(raw_layover.hotel_additional),
            transportation_additional=self.translate_transportation(
                raw_layover.transportation_additional
            ),
        )
        return compact_layover

    def translate_hotel(
        self, raw_hotel: raw.Hotel | raw.HotelAdditional | None
    ) -> compact.Hotel | None:
        if raw_hotel is None:
            return None
        return compact.Hotel(name=raw_hotel.name,phone=raw_hotel.phone)

    def translate_transportation(
        self, raw_trans: raw.Transportation | raw.TransportationAdditional | None
    ) -> compact.Transportation | None:
        if raw_trans is None:
            return None
        return compact.Transportation(name=raw_trans.name,phone=raw_trans.phone)

    def split_times(self, lclhbt: str, iata: str) -> compact.LclHbt:
        lcl_str, hbt_str = lclhbt.split("/")
        tz_str = self.tz_lookup(iata)
        local_time = datetime.strptime(lcl_str, TIME).time()
        hbt_time = datetime.strptime(hbt_str, TIME).time()
        return compact.LclHbt(lcl=local_time, hbt=hbt_time, tz_name=tz_str)


def complete_future_date(ref_date: date, future: str, strf: str) -> date:
    struct_t = time.strptime(future,format=strf)
    future_date = date(ref_date.year,struct_t.tm_mon,struct_t.tm_mday)
    if ref_date>future_date:
        return date(future_date.year+1,future_date.month,future_date.day)
    return future_date



def collect_calendar_entries(trip: raw.Trip) -> list[str]:
    """Make a list of the calendar entries for this trip."""
    calendar_strings: list[str] = []
    for dutyperiod in trip.dutyperiods:
        calendar_strings.append(dutyperiod.report.calendar)
        for flight in dutyperiod.flights:
            calendar_strings.append(flight.calendar)
        assert dutyperiod.release is not None
        calendar_strings.append(dutyperiod.release.calendar)
        if dutyperiod.layover:
            if dutyperiod.layover.hotel:
                calendar_strings.append(dutyperiod.layover.hotel.calendar)
            if dutyperiod.layover.transportation:
                calendar_strings.append(dutyperiod.layover.transportation.calendar)
            if dutyperiod.layover.hotel_additional:
                calendar_strings.append(dutyperiod.layover.hotel_additional.calendar)
            if dutyperiod.layover.transportation_additional:
                calendar_strings.append(
                    dutyperiod.layover.transportation_additional.calendar
                )
    assert trip.footer is not None
    calendar_strings.append(trip.footer.calendar)
    calendar_entries: list[str] = []
    for entry in calendar_strings:
        calendar_entries.extend(entry.split())
    return calendar_entries


def get_start_dates(
    from_date: date, to_date: date, calendar_entries: list[str]
) -> list[date]:
    """Builds a list of dates representing start dates for trips."""
    days = int((to_date - from_date) / timedelta(days=1)) + 1
    assert len(calendar_entries) == days
    indexed_days = list(
        index_and_filter_strings(strings=calendar_entries, string_filter=is_numeric)
    )
    start_dates: list[date] = []
    for indexed in indexed_days:
        start_date = from_date + timedelta(days=indexed.idx)
        start_dates.append(start_date)
    assert start_dates[0] >= from_date
    assert start_dates[-1] <= to_date
    return start_dates
