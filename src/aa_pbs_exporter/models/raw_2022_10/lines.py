# from dataclasses import dataclass

# from aa_pbs_exporter.snippets.parsing.parsed_indexed_string import ParsedIndexedString


# @dataclass
# class PageHeader1(ParsedIndexedString):
#     # source: IndexedString
#     pass


# @dataclass
# class PageHeader2(ParsedIndexedString):
#     # source: IndexedString
#     calendar_range: str


# @dataclass
# class HeaderSeparator(ParsedIndexedString):
#     # source: IndexedString
#     pass


# @dataclass
# class BaseEquipment(ParsedIndexedString):
#     # source: IndexedString
#     base: str
#     satelite_base: str
#     equipment: str


# @dataclass
# class TripHeader(ParsedIndexedString):
#     # source: IndexedString
#     number: str
#     ops_count: str
#     positions: str
#     operations: str
#     special_qualification: str
#     calendar: str


# @dataclass
# class DutyPeriodReport(ParsedIndexedString):
#     # source: IndexedString
#     report: str
#     calendar: str


# @dataclass
# class Flight(ParsedIndexedString):
#     # source: IndexedString
#     dutyperiod_idx: str
#     dep_arr_day: str
#     eq_code: str
#     flight_number: str
#     deadhead: str
#     departure_station: str
#     departure_time: str
#     meal: str
#     arrival_station: str
#     arrival_time: str
#     block: str
#     synth: str
#     ground: str
#     equipment_change: str
#     calendar: str


# @dataclass
# class DutyPeriodRelease(ParsedIndexedString):
#     # source: IndexedString
#     release: str
#     block: str
#     synth: str
#     total_pay: str
#     duty: str
#     flight_duty: str
#     calendar: str


# @dataclass
# class Hotel(ParsedIndexedString):
#     # source: IndexedString
#     layover_city: str
#     name: str
#     phone: str
#     rest: str
#     calendar: str


# @dataclass
# class HotelAdditional(ParsedIndexedString):
#     # source: IndexedString
#     layover_city: str
#     name: str
#     phone: str
#     calendar: str


# @dataclass
# class Transportation(ParsedIndexedString):
#     # source: IndexedString
#     name: str
#     phone: str
#     calendar: str


# @dataclass
# class TransportationAdditional(ParsedIndexedString):
#     # source: IndexedString
#     name: str
#     phone: str
#     calendar: str


# @dataclass
# class TripFooter(ParsedIndexedString):
#     # source: IndexedString
#     block: str
#     synth: str
#     total_pay: str
#     tafb: str
#     calendar: str


# @dataclass
# class TripSeparator(ParsedIndexedString):
#     # source: IndexedString
#     pass


# @dataclass
# class PageFooter(ParsedIndexedString):
#     # source: IndexedString
#     issued: str
#     effective: str
#     base: str
#     satelite_base: str
#     equipment: str
#     division: str
#     page: str


# @dataclass
# class PackageDate(ParsedIndexedString):
#     # source: IndexedString
#     month: str
#     year: str
