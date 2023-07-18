from importlib import resources
from logging import Logger
from pathlib import Path

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import parsers_td
from aa_pbs_exporter.pbs_2022_01.parser.parse_scheme_td import ParserLookupSingle
from aa_pbs_exporter.snippets.indexed_string.typedict.index_strings import index_strings
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser import serialize
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseException,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_file_to_json import (
    parse_file_to_json,
)
from tests.aa_pbs_exporter.resources.helpers_3 import (
    ParserTest,
    ResourceLocator,
    hashed_file_from_resource,
)

SERIALIZE_ONLY = False
RESOURCE_DIR = f"{__package__}.resources.line"


PARSER_TEST_DATA: list[ParserTest] = [
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "BaseEquipment_satellite_base.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "BaseEquipment_satellite_base.json"
        ),
        name="BaseEquipment",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.BaseEquipment()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "BaseEquipment_no_satellite_base.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "BaseEquipment_no_satellite_base.json"
        ),
        name="BaseEquipment",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.BaseEquipment()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "CalendarOnly_calendar_only.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "CalendarOnly_calendar_only.json"),
        name="CalendarOnly",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.CalendarOnly()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "DutyPeriodRelease_with_calendar.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "DutyPeriodRelease_with_calendar.json"
        ),
        name="DutyPeriodRelease",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.DutyPeriodRelease()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(
            RESOURCE_DIR, "DutyPeriodRelease_without_calendar.txt"
        ),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "DutyPeriodRelease_without_calendar.json"
        ),
        name="DutyPeriodRelease",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.DutyPeriodRelease()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(
            RESOURCE_DIR, "DutyPeriodReport_duty_period_report.txt"
        ),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "DutyPeriodReport_duty_period_report.json"
        ),
        name="DutyPeriodReport",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.DutyPeriodReport()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "Flight_ground_time_eq_change.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "Flight_ground_time_eq_change.json"
        ),
        name="Flight",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.Flight()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "FlightDeadhead_ground_time.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "FlightDeadhead_ground_time.json"),
        name="FlightDeadhead",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.FlightDeadhead()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "FlightDeadhead_no_ground_time.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "FlightDeadhead_no_ground_time.json"
        ),
        name="FlightDeadhead",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.FlightDeadhead()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "FlightDeadhead_alpha_eq_type.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "FlightDeadhead_alpha_eq_type.json"
        ),
        name="FlightDeadhead",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.FlightDeadhead()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(
            RESOURCE_DIR, "HeaderSeparator_header_separator.txt"
        ),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "HeaderSeparator_header_separator.json"
        ),
        name="HeaderSeparator",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.HeaderSeparator()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "Layover_hotel.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "Layover_hotel.json"),
        name="Hotel",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.Layover()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(
            RESOURCE_DIR, "HotelAdditional_hotel_additional.txt"
        ),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "HotelAdditional_hotel_additional.json"
        ),
        name="HotelAdditional",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.HotelAdditional()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "PageFooter_page_footer.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "PageFooter_page_footer.json"),
        name="PageFooter",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.PageFooter()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "PageHeader1_page_header_1.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "PageHeader1_page_header_1.json"),
        name="PageHeader1",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.PageHeader1()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "PageHeader2_page_header_2.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "PageHeader2_page_header_2.json"),
        name="PageHeader2",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.PageHeader2()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "Transportation_transportation.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "Transportation_transportation.json"
        ),
        name="Transportation",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.Transportation()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "TripFooter_trip_footer.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "TripFooter_trip_footer.json"),
        name="TripFooter",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.TripFooter()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "TripHeader_trip_header.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "TripHeader_trip_header.json"),
        name="TripHeader",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.TripHeader()),
        indexer=index_strings,
    ),
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "TripSeparator_trip_separator.txt"),
        result_data="",
        expected_data=ResourceLocator(
            RESOURCE_DIR, "TripSeparator_trip_separator.json"
        ),
        name="TripSeparator",
        category="line",
        parser_lookup=ParserLookupSingle(parsers_td.TripSeparator()),
        indexer=index_strings,
    ),
]
PARSER_FAIL_TEST_DATA = (
    ParserTest(
        input_data=ResourceLocator(RESOURCE_DIR, "fail.txt"),
        result_data="",
        expected_data=ResourceLocator(RESOURCE_DIR, "fail.json"),
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
    json_path = output_path / f"{test_data.expected_data.file}"
    debug_path = output_path / f"{test_data.expected_data.file}_debug.txt"
    hashed_file = hashed_file_from_resource(test_data.input_data)
    logger.info(f"Testing data from {hashed_file!r}")
    with resources.as_file(test_data.input_data.file_resource()) as file_in:
        result = parse_file_to_json(
            file_in=file_in,
            indexer=test_data.indexer,
            parser_lookup=test_data.parser_lookup,
            file_out=json_path,
            debug_out=debug_path,
            source=hashed_file,
        )
    if not SERIALIZE_ONLY:
        with resources.as_file(
            test_data.expected_data.file_resource()
        ) as expected_file:
            expected = serialize.load_from_json(file_in=expected_file)
        assert result == expected
        # assert False


@pytest.mark.parametrize("test_data", PARSER_FAIL_TEST_DATA)
def test_parser_fail(test_app_data_dir: Path, logger: Logger, test_data: ParserTest):
    output_path = test_app_data_dir / test_data.category / "fail"
    json_path = output_path / f"{test_data.expected_data.file}"
    debug_path = output_path / f"{test_data.expected_data.file}_debug.txt"
    with resources.as_file(test_data.input_data.file_resource()) as file_in:
        with pytest.raises(ParseException):
            result = parse_file_to_json(
                file_in=file_in,
                indexer=test_data.indexer,
                parser_lookup=test_data.parser_lookup,
                file_out=json_path,
                debug_out=debug_path,
            )


SINGLE = ParserTest(
    input_data=ResourceLocator(RESOURCE_DIR, "CalendarOnly_calendar_only.txt"),
    result_data="",
    expected_data=ResourceLocator(RESOURCE_DIR, "CalendarOnly_calendar_only.json"),
    name="CalendarOnly",
    category="line",
    parser_lookup=ParserLookupSingle(parsers_td.CalendarOnly()),
    indexer=index_strings,
)


def test_single(test_app_data_dir: Path, logger: Logger):
    output_path = test_app_data_dir / "single_parser" / SINGLE.category
    json_path = output_path / "single_parser" / f"{SINGLE.expected_data.file}"
    debug_path = (
        output_path / "single_parser" / f"{SINGLE.expected_data.file}_debug.txt"
    )
    hashed_file = hashed_file_from_resource(SINGLE.input_data)
    logger.info(f"Testing data from {hashed_file!r}")
    with resources.as_file(SINGLE.input_data.file_resource()) as file_in:
        result = parse_file_to_json(
            file_in=file_in,
            indexer=SINGLE.indexer,
            parser_lookup=SINGLE.parser_lookup,
            file_out=json_path,
            debug_out=debug_path,
            source=hashed_file,
        )
    if not SERIALIZE_ONLY:
        with resources.as_file(SINGLE.expected_data.file_resource()) as expected_file:
            expected = serialize.load_from_json(file_in=expected_file)
        assert result == expected
        # assert False


def test_line(logger: Logger):
    txt = "                                                                                       −− 17 18 19 20 21 22\n"
    indexed_string: IndexedStringDict = {
        "idx": 0,
        "txt": txt,
    }
    parser = parsers_td.CalendarOnly()
    result = parser.parse(indexed_string)
    print(f"{result!r}")
    # assert False
