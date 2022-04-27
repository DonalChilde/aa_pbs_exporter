from marshmallow import Schema, fields

from aa_pbs_exporter.models import bid_package as bp


class TransportationSchema(Schema):

    name = fields.String()
    phone = fields.String(missing=None)


class HotelSchema(Schema):
    pass
    # name = fields.String()
    # phone=fields.String(missing=None)
    # transportation: Optional["Transportation"] = None


class FlightSchema(Schema):
    pass
    # day = fields.String()
    # equipment_code = fields.String()
    # flight_number = fields.String()
    # deadhead: bool
    # departure_station = fields.String()
    # departure_local: time
    # departure_hbt: time
    # crewmeal = fields.String()
    # arrival_station = fields.String()
    # arrival_local: time
    # arrival_hbt: time
    # block: timedelta
    # synth: timedelta
    # ground: timedelta
    # equipment_change: bool


class DutyPeriodSchema(Schema):
    pass
    # report_local: time
    # report_hbt: time
    # release_local: time
    # release_hbt: time
    # block: timedelta
    # synth: timedelta
    # total_pay: timedelta
    # duty: timedelta
    # flight_duty: timedelta
    # rest: timedelta
    # flights: List["Flight"] = field(default_factory=list)
    # hotels: List["Hotel"] = field(default_factory=list)


class ThreePartStatusSchema(Schema):
    pass
    # base = fields.String()
    # equipment = fields.String()
    # division = fields.String()


class BidSequenceSchema(Schema):
    # three_part: ThreePartStatus | None
    sequence_number = fields.String()
    ops_count = fields.Integer()
    # total_block: timedelta
    # synth: timedelta
    # total_pay: timedelta
    # tafb: timedelta
    # internal_page: int
    # from_line: int
    # to_line: int
    # positions: Set[str] = field(default_factory=set)
    # operations: Set[str] = field(default_factory=set)
    # special_qualification: bool = False
    # start_dates: List[date] = field(default_factory=list)
    # duty_periods: List["DutyPeriod"] = field(default_factory=list)
    # prior_month_sequence= fields.String(missing=None)
    # prior_month_date= fields.String(missing=None)


class BidPackageSchema(Schema):
    date_from = fields.Date()
    date_to = fields.Date()
    base = fields.List(fields.String())
    equipment = fields.List(fields.String())
    satelite_bases = fields.List(fields.String())
    bid_sequences = fields.List(fields.Nested(BidSequenceSchema()))
    source = fields.String()
