from uuid import uuid5

from aa_pbs_exporter.pbs_2022_01 import validate
from aa_pbs_exporter.pbs_2022_01.helpers.collect_calendar_entries import (
    collect_calendar_entries,
)
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile


class ParsedToRaw:
    def __init__(
        self, source: HashedFile | None, validator: validate.RawValidator | None
    ) -> None:
        self.source = source
        self.validator = validator
        if source:
            uuid_seed = source.file_hash
        else:
            uuid_seed = "None"
        uuid = uuid5(raw.BIDPACKAGE_DNS, uuid_seed)
        self.bid_package = raw.BidPackage(uuid=uuid, source=source, pages=[])

    def page_header1(self, parsed: raw.PageHeader1):
        page = raw.Page(uuid=parsed.uuid5(), page_header_1=parsed, trips=[])
        self.bid_package.pages.append(page)

    def page_header2(self, parsed: raw.PageHeader2):
        self.bid_package.pages[-1].page_header_2 = parsed

    def header_separator(self, parsed: raw.HeaderSeparator):
        pass

    def base_equipment(self, parsed: raw.BaseEquipment):
        self.bid_package.pages[-1].base_equipment = parsed

    def trip_header(self, parsed: raw.TripHeader):
        print("ptr", parsed.str_with_uuid())
        print("ptr", parsed.uuid5())
        trip = raw.Trip(uuid=parsed.uuid5(), header=parsed, dutyperiods=[])
        self.bid_package.pages[-1].trips.append(trip)

    def duty_period_report(self, parsed: raw.DutyPeriodReport):
        dutyperiod = raw.DutyPeriod(uuid=parsed.uuid5(), report=parsed, flights=[])
        self.bid_package.pages[-1].trips[-1].dutyperiods.append(dutyperiod)

    def flight(self, parsed: raw.Flight):
        self.bid_package.pages[-1].trips[-1].dutyperiods[-1].flights.append(parsed)

    def duty_period_release(self, parsed: raw.DutyPeriodRelease):
        self.bid_package.pages[-1].trips[-1].dutyperiods[-1].release = parsed

    def hotel(self, parsed: raw.Hotel):
        layover = raw.Layover(uuid=parsed.uuid5(), hotel=parsed)
        layover.uuid = layover.uuid5()
        self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover = layover

    def hotel_additional(self, parsed: raw.HotelAdditional):
        layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
        assert layover is not None
        layover.hotel_additional = parsed

    def transportation(self, parsed: raw.Transportation):
        layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
        assert layover is not None
        layover.transportation = parsed

    def transportation_additional(self, parsed: raw.TransportationAdditional):
        layover = self.bid_package.pages[-1].trips[-1].dutyperiods[-1].layover
        assert layover is not None
        layover.transportation_additional = parsed

    def calendar_only(self, parsed: raw.CalendarOnly):
        self.bid_package.pages[-1].trips[-1].calendar_only = parsed

    def trip_footer(self, parsed: raw.TripFooter):
        self.bid_package.pages[-1].trips[-1].footer = parsed

    def trip_separator(self, parsed: raw.TripSeparator):
        pass

    def page_footer(self, parsed: raw.PageFooter):
        self.bid_package.pages[-1].page_footer = parsed

    def parse_complete(self, ctx: dict | None = None):
        for trip in self.bid_package.walk_trips():
            trip.calendar_entries = collect_calendar_entries(trip)
        if self.validator is not None:
            self.validator.validate_bid_package(bid_package=self.bid_package, ctx=ctx)

    # def package_date(self, parsed: raw.PackageDate):
    #     pass
