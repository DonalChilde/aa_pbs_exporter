from uuid import uuid5

from aa_pbs_exporter.pbs_2022_01 import PARSER_DNS, validate
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
from aa_pbs_exporter.pbs_2022_01.raw_helpers import collect_calendar_entries


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
        page = raw.Page(uuid=PARSER_DNS, page_header_1=parsed, trips=[])
        page.uuid = page.uuid5()
        self.bid_package.pages.append(page)

    def page_header2(self, parsed: raw.PageHeader2):
        self.bid_package.pages[-1].page_header_2 = parsed

    def header_separator(self, parsed: raw.HeaderSeparator):
        pass

    def base_equipment(self, parsed: raw.BaseEquipment):
        self.bid_package.pages[-1].base_equipment = parsed

    def trip_header(self, parsed: raw.TripHeader):
        trip = raw.Trip(uuid=PARSER_DNS, header=parsed, dutyperiods=[])
        trip.uuid = trip.uuid5()
        self.bid_package.pages[-1].trips.append(trip)

    def duty_period_report(self, parsed: raw.DutyPeriodReport):
        dutyperiod = raw.DutyPeriod(uuid=PARSER_DNS, report=parsed, flights=[])
        dutyperiod.uuid = dutyperiod.uuid5()
        self.bid_package.pages[-1].trips[-1].dutyperiods.append(dutyperiod)

    def flight(self, parsed: raw.Flight):
        self.bid_package.pages[-1].trips[-1].dutyperiods[-1].flights.append(parsed)

    def duty_period_release(self, parsed: raw.DutyPeriodRelease):
        self.bid_package.pages[-1].trips[-1].dutyperiods[-1].release = parsed

    def hotel(self, parsed: raw.Hotel):
        layover = raw.Layover(uuid=PARSER_DNS, hotel=parsed)
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
