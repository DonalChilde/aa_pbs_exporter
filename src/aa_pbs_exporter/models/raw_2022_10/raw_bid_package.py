from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Sequence

from aa_pbs_exporter.models.raw_2022_10.raw_lines import (
    BaseEquipment,
    DutyPeriodRelease,
    DutyPeriodReport,
    Flight,
    Hotel,
    HotelAdditional,
    PageFooter,
    PageHeader1,
    PageHeader2,
    Transportation,
    TransportationAdditional,
    TripFooter,
    TripHeader,
)
from aa_pbs_exporter.models.raw_2022_10.translate import extract_start_dates
from aa_pbs_exporter.util.dataclass_repr_mixin import DataclassReprMixin


@dataclass
class DutyPeriod(DataclassReprMixin):
    report: DutyPeriodReport
    release: DutyPeriodRelease | None = None
    hotel: Hotel | None = None
    transportation: Transportation | None = None
    hotel_additional: HotelAdditional | None = None
    transportation_additional: TransportationAdditional | None = None
    flights: List[Flight] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()


@dataclass
class Trip(DataclassReprMixin):
    header: TripHeader
    footer: TripFooter | None = None
    # calendar: List = field(default_factory=list)
    dutyperiods: List[DutyPeriod] = field(default_factory=list)

    def __repr__(self):  # pylint: disable=useless-parent-delegation
        return super().__repr__()

    def start_dates(self, effective: datetime, from_to: str) -> Sequence[datetime]:
        return extract_start_dates(trip=self, effective=effective, from_to=from_to)


@dataclass
class Page(DataclassReprMixin):
    page_header_1: PageHeader1
    page_header_2: PageHeader2 | None = None
    base_equipment: BaseEquipment | None = None
    page_footer: PageFooter | None = None
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
