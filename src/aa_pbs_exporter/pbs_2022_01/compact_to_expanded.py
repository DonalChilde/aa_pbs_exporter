from datetime import date, datetime, time, timedelta
from typing import Sequence
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from zoneinfo import ZoneInfo


class Translator:
    def __init__(self) -> None:
        pass

    def translate(self, compact_bid_package: compact.BidPackage) -> expanded.BidPackage:
        expanded_bid_package = expanded.BidPackage(
            source=compact_bid_package.source, pages=[]
        )
        for compact_page in compact_bid_package.pages:
            expanded_bid_package.pages.append(self.translate_page(compact_page))
        return expanded_bid_package

    def translate_page(self, compact_page: compact.Page) -> expanded.Page:
        expanded_page = expanded.Page(
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
            start = datetime.combine(
                start_date,
                compact_trip.dutyperiods[0].report.lcl,
                ZoneInfo(compact_trip.dutyperiods[0].report.tz_str),
            )

        return trips

    def translate_dutyperiod(
        self, ref_date: date, compact_dutyperiod: compact.DutyPeriod
    ) -> expanded.DutyPeriod:
        report = datetime.combine(
            ref_date,
            compact_dutyperiod.report.lcl,
            ZoneInfo(compact_dutyperiod.report.tz_str),
        )
        release = complete_future_time(
            report, compact_dutyperiod.release.lcl, compact_dutyperiod.release.tz_str
        )
        expanded_dutyperiod = expanded.DutyPeriod()

        return expanded_dutyperiod

    def translate_flight(self, compact_flight: compact.Flight) -> expanded.Flight:
        expanded_flight = expanded.Flight()

        return expanded_flight

    def translate_layover(self, compact_layover: compact.Layover) -> expanded.Layover:
        expanded_layover = expanded.Layover()

        return expanded_layover

    def translate_hotel(self, compact_hotel: compact.Hotel) -> expanded.Hotel:
        expanded_hotel = expanded.Hotel()

        return expanded_hotel

    def translate_tranportation(
        self, compact_transportation: compact.Transportation
    ) -> expanded.Transportation:
        expanded_transportation = expanded.Transportation()

        return expanded_transportation


def complete_future_time(
    ref_datetime: datetime, future_time: time, future_tz_str: str
) -> datetime:
    """
    _summary_

    Does not handle fold - timezone overlaps
    

    Args:
        ref_datetime: _description_
        future_time: _description_
        future_tz_str: _description_

    Returns:
        _description_
    """
    future_tz = ZoneInfo(future_tz_str)
    future_ref = ref_datetime.astimezone(future_tz)
    future_datetime = future_ref.replace(
        hour=future_time.hour,
        minute=future_time.minute,
        second=future_time.second,
        microsecond=future_time.microsecond,
    )
    if future_datetime<future_ref:
        return future_datetime+timedelta(days=1)
    return future_datetime