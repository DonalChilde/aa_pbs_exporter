from dataclasses import dataclass

from aa_pbs_exporter.util.dataclass_repr_mixin import DataclassReprMixin


@dataclass
class SourceText(DataclassReprMixin):
    line_no: int
    txt: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class PageHeader1(DataclassReprMixin):
    source: SourceText

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class PageHeader2(DataclassReprMixin):
    source: SourceText
    calendar_range: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class HeaderSeparator(DataclassReprMixin):
    source: SourceText

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class BaseEquipment(DataclassReprMixin):
    source: SourceText
    base: str
    satelite_base: str
    equipment: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class TripHeader(DataclassReprMixin):
    source: SourceText
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
    source: SourceText
    report: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class Flight(DataclassReprMixin):
    source: SourceText
    dutyperiod_index: str
    d_a: str
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
    source: SourceText
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
    source: SourceText
    layover_city: str
    name: str
    phone: str
    rest: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class HotelAdditional(DataclassReprMixin):
    source: SourceText
    layover_city: str
    name: str
    phone: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class Transportation(DataclassReprMixin):
    source: SourceText
    name: str
    phone: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class TransportationAdditional(DataclassReprMixin):
    source: SourceText
    name: str
    phone: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class TripFooter(DataclassReprMixin):
    source: SourceText
    block: str
    synth: str
    total_pay: str
    tafb: str
    calendar: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class TripSeparator(DataclassReprMixin):
    source: SourceText

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class PageFooter(DataclassReprMixin):
    source: SourceText
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
    source: SourceText
    month: str
    year: str

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()
