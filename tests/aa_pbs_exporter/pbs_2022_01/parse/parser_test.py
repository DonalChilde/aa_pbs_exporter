from importlib import resources
from logging import Logger
from pathlib import Path

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import parsers_td
from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme_td import ParserLookupSingle
from aa_pbs_exporter.snippets.indexed_string.typedict.index_strings import index_strings
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser import serialize
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseException,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_file_to_json import (
    parse_file_to_json,
)
from tests.aa_pbs_exporter.resources.helpers_3 import ParserTest

SERIALIZE_ONLY = False


PARSER_TEST_DATA: list[ParserTest] = [
    ParserTest(
        input_data="satellite_base.txt",
        result_data="satellite_base.json",
        expected_data="satellite_base.json",
        resource_package=f"{__package__}.resources",
        name="BaseEquipment",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.BaseEquipment()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="no_satellite_base.txt",
        result_data="no_satellite_base.json",
        expected_data="no_satellite_base.json",
        resource_package=f"{__package__}.resources",
        name="BaseEquipment",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.BaseEquipment()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="calendar_only.txt",
        result_data="calendar_only.json",
        expected_data="calendar_only.json",
        resource_package=f"{__package__}.resources",
        name="CalendarOnly",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.CalendarOnly()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="with_calendar.txt",
        result_data="with_calendar.json",
        expected_data="with_calendar.json",
        resource_package=f"{__package__}.resources",
        name="DutyPeriodRelease",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.DutyPeriodRelease()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="without_calendar.txt",
        result_data="without_calendar.json",
        expected_data="without_calendar.json",
        resource_package=f"{__package__}.resources",
        name="DutyPeriodRelease",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.DutyPeriodRelease()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="duty_period_report.txt",
        result_data="duty_period_report.json",
        expected_data="duty_period_report.json",
        resource_package=f"{__package__}.resources",
        name="DutyPeriodReport",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.DutyPeriodReport()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="ground_time_eq_change.txt",
        result_data="ground_time_eq_change.json",
        expected_data="ground_time_eq_change.json",
        resource_package=f"{__package__}.resources",
        name="Flight",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.Flight()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="ground_time.txt",
        result_data="ground_time.json",
        expected_data="ground_time.json",
        resource_package=f"{__package__}.resources",
        name="FlightDeadhead",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.FlightDeadhead()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="no_ground_time.txt",
        result_data="no_ground_time.json",
        expected_data="no_ground_time.json",
        resource_package=f"{__package__}.resources",
        name="FlightDeadhead",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.FlightDeadhead()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="alpha_eq_type.txt",
        result_data="alpha_eq_type.json",
        expected_data="alpha_eq_type.json",
        resource_package=f"{__package__}.resources",
        name="FlightDeadhead",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.FlightDeadhead()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="header_separator.txt",
        result_data="header_separator.json",
        expected_data="header_separator.json",
        resource_package=f"{__package__}.resources",
        name="HeaderSeparator",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.HeaderSeparator()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="hotel.txt",
        result_data="hotel.json",
        expected_data="hotel.json",
        resource_package=f"{__package__}.resources",
        name="Hotel",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.Hotel()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="hotel_additional.txt",
        result_data="hotel_additional.json",
        expected_data="hotel_additional.json",
        resource_package=f"{__package__}.resources",
        name="HotelAdditional",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.HotelAdditional()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="page_footer.txt",
        result_data="page_footer.json",
        expected_data="page_footer.json",
        resource_package=f"{__package__}.resources",
        name="PageFooter",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.PageFooter()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="page_header_1.txt",
        result_data="page_header_1.json",
        expected_data="page_header_1.json",
        resource_package=f"{__package__}.resources",
        name="PageHeader1",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.PageHeader1()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="page_header_2.txt",
        result_data="page_header_2.json",
        expected_data="page_header_2.json",
        resource_package=f"{__package__}.resources",
        name="PageHeader2",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.PageHeader2()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="transportation.txt",
        result_data="transportation.json",
        expected_data="transportation.json",
        resource_package=f"{__package__}.resources",
        name="Transportation",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.Transportation()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="trip_footer.txt",
        result_data="trip_footer.json",
        expected_data="trip_footer.json",
        resource_package=f"{__package__}.resources",
        name="TripFooter",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.TripFooter()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="trip_header.txt",
        result_data="trip_header.json",
        expected_data="trip_header.json",
        resource_package=f"{__package__}.resources",
        name="TripHeader",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.TripHeader()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data="trip_separator.txt",
        result_data="trip_separator.json",
        expected_data="trip_separator.json",
        resource_package=f"{__package__}.resources",
        name="TripSeparator",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.TripSeparator()),
        indexer=index_strings,
    ),
]
PARSER_FAIL_TEST_DATA = (
    ParserTest(
        input_data="fail.txt",
        result_data="fail.json",
        expected_data="fail.json",
        resource_package=f"{__package__}.resources",
        name="BaseEquipment",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.BaseEquipment()),
        indexer=index_strings,
    ),
)

# TODO make a fail list for a list of parsers, to save space and complexity


@pytest.mark.parametrize("test_data", PARSER_TEST_DATA)
def test_parser(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category
    res_dir = resources.files(f"{test_data.resource_package}.{test_data.category}")
    res_file = res_dir.joinpath(f"{test_data.name}_{test_data.input_data}")
    json_path = output_path / f"{test_data.name}_{test_data.result_data}"
    debug_path = output_path / f"{test_data.name}_{test_data.input_data}_debug.txt"
    with resources.as_file(res_file) as file_in:
        result = parse_file_to_json(
            file_in=file_in,
            indexer=test_data.indexer,
            parser_lookup=test_data.parser_lookup,
            file_out=json_path,
            debug_out=debug_path,
        )
    if not SERIALIZE_ONLY:
        expected_res = res_dir.joinpath(f"{test_data.name}_{test_data.result_data}")
        with resources.as_file(expected_res) as expected_file:
            expected = serialize.load_from_json(file_in=expected_file)
        assert result == expected


@pytest.mark.parametrize("test_data", PARSER_FAIL_TEST_DATA)
def test_parser_fail(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category / "fail"
    res_dir = resources.files(f"{test_data.resource_package}.{test_data.category}")
    print("Package Name:", test_data.resource_package)
    res_file = res_dir.joinpath(test_data.input_data)
    json_path = output_path / f"{test_data.name}_{test_data.result_data}"
    debug_path = output_path / f"{test_data.name}_{test_data.input_data}_debug.txt"
    with resources.as_file(res_file) as file_in:
        with pytest.raises(ParseException):
            result = parse_file_to_json(
                file_in=file_in,
                indexer=test_data.indexer,
                parser_lookup=test_data.parser_lookup,
                file_out=json_path,
                debug_out=debug_path,
            )
