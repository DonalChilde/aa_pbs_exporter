from datetime import datetime, time, timedelta, timezone
from typing import Sequence
from uuid import uuid5
from zoneinfo import ZoneInfo

from aa_pbs_exporter.pbs_2022_01 import validate
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.pbs_2022_01.models.common import Instant


class CompactToExpanded:
    def __init__(
        self,
        validator: validate.ExpandedValidator | None = None,
    ) -> None:
        self.validator = validator

    def translate(self, compact_bid_package: compact.BidPackage) -> expanded.BidPackage:
        expanded_bid_package = expanded.BidPackage(
            uuid=compact_bid_package.uuid, source=compact_bid_package.source, pages=[]
        )
        for compact_page in compact_bid_package.pages:
            expanded_bid_package.pages.append(self.translate_page(compact_page))
        return expanded_bid_package

    def translate_page(self, compact_page: compact.Page) -> expanded.Page:
        expanded_page = expanded.Page(
            uuid=compact_page.uuid,
            base=compact_page.base,
            satellite_base=compact_page.satellite_base,
            equipment=compact_page.equipment,
            division=compact_page.division,
            issued=compact_page.issued,
            effective=compact_page.effective,
            start=compact_page.start,
            end=compact_page.end,
            trips=[],
        )
        for compact_trip in compact_page.trips:
            expanded_page.trips.extend(self.translate_trip(compact_trip))

        return expanded_page

    def translate_trip(self, compact_trip: compact.Trip) -> Sequence[expanded.Trip]:
        trips = []
        for start_date in compact_trip.start_dates:
            # NOTE Does not account for times in the fold
            start_utc = datetime.combine(
                start_date,
                compact_trip.dutyperiods[0].report.lcl,
                ZoneInfo(compact_trip.dutyperiods[0].report.tz_name),
            ).astimezone(timezone.utc)
            start = Instant(
                utc_date=start_utc,
                tz_name=compact_trip.dutyperiods[0].report.tz_name,
            )
            end = start + compact_trip.tafb
            expanded_trip = expanded.Trip(
                uuid=uuid5(compact_trip.uuid, start.utc_date.isoformat()),
                compact_uuid=compact_trip.uuid,
                number=compact_trip.number,
                start=start,
                end=end,
                positions=list(compact_trip.positions),
                operations=compact_trip.operations,
                special_qualifications=compact_trip.special_qualifications,
                block=compact_trip.block,
                synth=compact_trip.synth,
                total_pay=compact_trip.total_pay,
                tafb=compact_trip.tafb,
                dutyperiods=[],
            )
            dutyperiod_ref_instant = start + timedelta()
            for compact_dutyperiod in compact_trip.dutyperiods:
                expanded_dutyperiod = self.translate_dutyperiod(
                    report=dutyperiod_ref_instant, compact_dutyperiod=compact_dutyperiod
                )
                if expanded_dutyperiod.layover is not None:
                    dutyperiod_ref_instant = (
                        expanded_dutyperiod.release + expanded_dutyperiod.layover.odl
                    )
                expanded_trip.dutyperiods.append(expanded_dutyperiod)
            trips.append(expanded_trip)
        return trips

    def translate_dutyperiod(
        self,
        report: Instant,
        compact_dutyperiod: compact.DutyPeriod,
    ) -> expanded.DutyPeriod:
        release_utc = report.utc_date + compact_dutyperiod.duty
        release = Instant(
            utc_date=release_utc, tz_name=compact_dutyperiod.release.tz_name
        )

        expanded_dutyperiod = expanded.DutyPeriod(
            uuid=uuid5(compact_dutyperiod.uuid, report.utc_date.isoformat()),
            compact_uuid=compact_dutyperiod.uuid,
            idx=compact_dutyperiod.idx,
            report=report,
            report_station=compact_dutyperiod.report_station,
            release=release,
            release_station=compact_dutyperiod.release_station,
            block=compact_dutyperiod.block,
            synth=compact_dutyperiod.synth,
            total_pay=compact_dutyperiod.total_pay,
            duty=compact_dutyperiod.duty,
            flight_duty=compact_dutyperiod.flight_duty,
            layover=self.translate_layover(compact_dutyperiod.layover),
            flights=[],
        )
        flight_ref_instant = expanded_dutyperiod.report
        for flight in compact_dutyperiod.flights:
            expanded_flight = self.translate_flight(flight_ref_instant, flight)
            expanded_dutyperiod.flights.append(expanded_flight)
            flight_ref_instant = expanded_flight.arrival + expanded_flight.ground
        self.validate_dutyperiod(compact_dutyperiod, expanded_dutyperiod)
        return expanded_dutyperiod

    def validate_dutyperiod(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
    ):
        # TODO make validation exception, raise on error
        assert compare_time(
            expanded_dutyperiod.release.local().time(),
            compact_dutyperiod.release.lcl,
            ignore_tz=True,
        )

    def translate_flight(
        self, ref_instant: Instant, compact_flight: compact.Flight
    ) -> expanded.Flight:
        departure = complete_time_instant(
            ref_instant=ref_instant,
            new_time=compact_flight.departure.lcl,
            new_tz_name=compact_flight.departure.tz_name,
        )
        arrival = self.calculate_arrival(departure, compact_flight)
        expanded_flight = expanded.Flight(
            uuid=uuid5(compact_flight.uuid, departure.utc_date.isoformat()),
            compact_uuid=compact_flight.uuid,
            dp_idx=compact_flight.dp_idx,
            idx=compact_flight.idx,
            dep_arr_day=compact_flight.dep_arr_day,
            eq_code=compact_flight.eq_code,
            number=compact_flight.number,
            deadhead=compact_flight.deadhead,
            departure_station=compact_flight.departure_station,
            departure=departure,
            meal=compact_flight.meal,
            arrival_station=compact_flight.arrival_station,
            arrival=arrival,
            block=compact_flight.block,
            synth=compact_flight.synth,
            ground=compact_flight.ground,
            equipment_change=compact_flight.equipment_change,
        )

        self.validate_flight(compact_flight, expanded_flight)
        return expanded_flight

    def validate_flight(
        self, compact_flight: compact.Flight, expanded_flight: expanded.Flight
    ):
        assert compare_time(
            expanded_flight.arrival.local().time(),
            compact_flight.arrival.lcl,
            ignore_tz=True,
        )

    def calculate_arrival(
        self,
        departure: Instant,
        compact_flight: compact.Flight,
    ) -> Instant:
        if not compact_flight.deadhead:
            arrival_time = departure + compact_flight.block
        else:
            # NOTE not sure if this is true in all cases
            arrival_time = departure + compact_flight.synth
        return arrival_time.new_tz(compact_flight.arrival.tz_name)

    def translate_layover(
        self, compact_layover: compact.Layover | None
    ) -> expanded.Layover | None:
        if compact_layover is None:
            return None
        expanded_layover = expanded.Layover(
            uuid=compact_layover.uuid,
            odl=compact_layover.odl,
            city=compact_layover.city,
            hotel=self.translate_hotel(compact_layover.hotel),
            transportation=self.translate_tranportation(compact_layover.transportation),
            hotel_additional=self.translate_hotel(compact_layover.hotel_additional),
            transportation_additional=self.translate_tranportation(
                compact_layover.transportation_additional
            ),
        )
        return expanded_layover

    def translate_hotel(
        self, compact_hotel: compact.Hotel | None
    ) -> expanded.Hotel | None:
        if compact_hotel is None:
            return None
        expanded_hotel = expanded.Hotel(
            uuid=compact_hotel.uuid, name=compact_hotel.name, phone=compact_hotel.phone
        )
        return expanded_hotel

    def translate_tranportation(
        self, compact_transportation: compact.Transportation | None
    ) -> expanded.Transportation | None:
        if compact_transportation is None:
            return None
        expanded_transportation = expanded.Transportation(
            uuid=compact_transportation.uuid,
            name=compact_transportation.name,
            phone=compact_transportation.phone,
        )
        return expanded_transportation


def add_timedelta(
    ref_datetime: datetime, t_delta: timedelta, *, utc_out: bool = False
) -> datetime:
    # TODO make snippet
    """
    Combine an aware datetime with a timedelta. Enforce utc manipulation.

    _extended_summary_

    Args:
        ref_datetime: _description_
        t_delta: _description_
        utc_out: _description_. Defaults to False.

    Raises:
        ValueError: _description_

    Returns:
        _description_
    """
    if ref_datetime.tzinfo is None:
        raise ValueError(
            f"ref_datetime: {ref_datetime!r} must be tz aware. No tzinfo found"
        )
    ref_tz = ref_datetime.tzinfo
    utc_ref = ref_datetime.astimezone(timezone.utc)
    utc_delta = utc_ref + t_delta
    if utc_out:
        return utc_delta
    return utc_delta.astimezone(ref_tz)


def complete_time_instant(
    ref_instant: Instant,
    new_time: time,
    new_tz_name: str,
    is_future: bool = True,
) -> Instant:
    # TODO make snippet
    new_datetime = complete_time(
        ref_datetime=ref_instant.utc_date,
        new_time=new_time,
        new_tz_name=new_tz_name,
        is_future=is_future,
    )
    return Instant(utc_date=new_datetime.astimezone(timezone.utc), tz_name=new_tz_name)


def replace_time(
    ref_datetime: datetime, new_time: time, use_time_tz: bool = False
) -> datetime:
    # TODO make snippet
    if use_time_tz:
        tzinfo = new_time.tzinfo
    else:
        tzinfo = ref_datetime.tzinfo
    new_datetime = ref_datetime.replace(
        hour=new_time.hour,
        minute=new_time.minute,
        second=new_time.second,
        microsecond=new_time.microsecond,
        tzinfo=tzinfo,
    )
    return new_datetime


def compare_time(alpha: time, beta: time, ignore_tz: bool = False) -> bool:
    # TODO make snippet
    if ignore_tz:
        alpha_n = alpha.replace(tzinfo=None)
        beta_n = beta.replace(tzinfo=None)
        return alpha_n == beta_n
    return alpha == beta


# def complete_future_time(
#     ref_datetime: datetime, future_time: time, future_tz_str: str
# ) -> datetime:
#     """
#     _summary_

#     Does not handle fold - timezone overlaps


#     Args:
#         ref_datetime: _description_
#         future_time: _description_
#         future_tz_str: _description_

#     Returns:
#         _description_
#     """
#     if ref_datetime.tzinfo is None:
#         raise ValueError(
#             f"ref_datetime: {ref_datetime!r} must be tz aware. No tzinfo found"
#         )
#     future_tz = ZoneInfo(future_tz_str)
#     future_ref = ref_datetime.astimezone(future_tz)
#     future_datetime = replace_time(future_ref, future_time)
#     if future_datetime < future_ref:
#         return future_datetime + timedelta(days=1)
#     return future_datetime


def complete_time(
    ref_datetime: datetime, new_time: time, new_tz_name: str, is_future: bool = True
) -> datetime:
    # TODO make snippet
    if ref_datetime.tzinfo is None:
        raise ValueError(
            f"ref_datetime: {ref_datetime!r} must be tz aware. No tzinfo found"
        )
    new_tzinfo = ZoneInfo(new_tz_name)
    localized_ref = ref_datetime.astimezone(new_tzinfo)
    new_datetime = replace_time(localized_ref, new_time)
    if is_future:
        if new_datetime < localized_ref:
            return new_datetime + timedelta(days=1)
        return new_datetime
    if new_datetime > localized_ref:
        return new_datetime - timedelta(days=1)
    return new_datetime
