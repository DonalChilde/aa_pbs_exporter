from typing import TypedDict


class PageHeader1(TypedDict):
    pass


class PageHeader2(TypedDict):
    from_date: str
    to_date: str


class HeaderSeparator(TypedDict):
    pass


class BaseEquipment(TypedDict):
    base: str
    satellite_base: str
    equipment: str


class TripHeader(TypedDict):
    number: str
    ops_count: str
    positions: str
    operations: str
    qualifications: str


class PriorMonthDeadhead(TypedDict):
    pass


class DutyPeriodReport(TypedDict):
    report: str
    calendar: list[str]


class Flight(TypedDict):
    dutyperiod_idx: str
    dep_arr_day: str
    eq_code: str
    flight_number: str
    deadhead: str
    departure_station: str
    departure_time: str
    meal: str
    arrival_station: str
    arrival_time: str
    block: str
    synth: str
    ground: str
    equipment_change: str
    calendar: list[str]


class DutyPeriodRelease(TypedDict):
    release: str
    block: str
    synth: str
    total_pay: str
    duty: str
    flight_duty: str
    calendar: list[str]


class Layover(TypedDict):
    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: list[str]


class HotelAdditional(TypedDict):
    layover_city: str
    name: str
    phone: str
    calendar: list[str]


class Transportation(TypedDict):
    name: str
    phone: str
    calendar: list[str]


class TransportationAdditional(TypedDict):
    name: str
    phone: str
    calendar: list[str]


class TripFooter(TypedDict):
    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: list[str]


class CalendarOnly(TypedDict):
    calendar: list[str]


class TripSeparator(TypedDict):
    pass


class PageFooter(TypedDict):
    issued: str
    effective: str
    base: str
    satelite_base: str
    equipment: str
    division: str
    page: str


class Stats:
    # TODO usd this class to generate stats
    pass
