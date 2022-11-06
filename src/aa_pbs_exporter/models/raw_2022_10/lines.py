from dataclasses import dataclass

from aa_pbs_exporter.util.dataclass_repr_mixin import DataclassReprMixin
from aa_pbs_exporter.util.indexed_string import IndexedString


@dataclass
class PageHeader1(DataclassReprMixin):
    source: IndexedString

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class PageHeader2(DataclassReprMixin):
    source: IndexedString
    calendar_range: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class HeaderSeparator(DataclassReprMixin):
    source: IndexedString

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class BaseEquipment(DataclassReprMixin):
    source: IndexedString
    base: str
    satelite_base: str
    equipment: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class TripHeader(DataclassReprMixin):
    source: IndexedString
    number: str
    ops_count: str
    positions: str
    operations: str
    special_qualification: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class DutyPeriodReport(DataclassReprMixin):
    source: IndexedString
    report: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class Flight(DataclassReprMixin):
    source: IndexedString
    dutyperiod_index: str
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
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class DutyPeriodRelease(DataclassReprMixin):
    source: IndexedString
    release: str
    block: str
    synth: str
    total_pay: str
    duty: str
    flight_duty: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class Hotel(DataclassReprMixin):
    source: IndexedString
    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class HotelAdditional(DataclassReprMixin):
    source: IndexedString
    layover_city: str
    name: str
    phone: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class Transportation(DataclassReprMixin):
    source: IndexedString
    name: str
    phone: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class TransportationAdditional(DataclassReprMixin):
    source: IndexedString
    name: str
    phone: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class TripFooter(DataclassReprMixin):
    source: IndexedString
    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class TripSeparator(DataclassReprMixin):
    source: IndexedString

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class PageFooter(DataclassReprMixin):
    source: IndexedString
    issued: str
    effective: str
    base: str
    satelite_base: str
    equipment: str
    division: str
    page: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class PackageDate(DataclassReprMixin):
    source: IndexedString
    month: str
    year: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()
