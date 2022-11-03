from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from aa_pbs_exporter.models.raw_2022_10 import raw_lines
from aa_pbs_exporter.util.dataclass_repr_mixin import DataclassReprMixin


@dataclass
class DutyPeriod(DataclassReprMixin):
    report: raw_lines.DutyPeriodReport
    release: raw_lines.DutyPeriodRelease | None = None
    hotel: raw_lines.Hotel | None = None
    transportation: raw_lines.Transportation | None = None
    hotel_additional: raw_lines.HotelAdditional | None = None
    transportation_additional: raw_lines.TransportationAdditional | None = None
    flights: List[raw_lines.Flight] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class Trip(DataclassReprMixin):
    header: raw_lines.TripHeader
    footer: raw_lines.TripFooter | None = None
    # calendar: List = field(default_factory=list)
    dutyperiods: List[DutyPeriod] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class Page(DataclassReprMixin):
    page_header_1: raw_lines.PageHeader1
    page_header_2: raw_lines.PageHeader2 | None = None
    base_equipment: raw_lines.BaseEquipment | None = None
    page_footer: raw_lines.PageFooter | None = None
    trips: List[Trip] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def effective(self) -> datetime:
        if self.page_footer is not None:
            return datetime.strptime(self.page_footer.effective, "%d&b%Y")
        raise ValueError("Tried to get effective date, but page_footer was None.")

    def from_to(self) -> str:
        if self.page_header_2 is None:
            raise ValueError("Tried to get from_to but page_header_2 was None.")
        return self.page_header_2.calendar_range


@dataclass
class Package(DataclassReprMixin):
    file_name: str
    # package_date: PackageDate | None
    pages: List[Page] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()
