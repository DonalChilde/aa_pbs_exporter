from logging import Logger
from pathlib import Path

import pytest
from tests.aa_pbs_exporter.resources.helpers_2 import ResourceTestData, process_lines

from aa_pbs_exporter.pbs_2022_01 import parsers
from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_exception import (
    ParseException,
)

PARSER = parsers.BaseEquipment()
MODEL = raw.BaseEquipment
SERIALIZE_ONLY = False
TEST_DATA = [
    ResourceTestData("satellite_base.txt", "satellite_base.json"),
    ResourceTestData("no_satellite_base.txt", "no_satellite_base.json"),
]


TEST_FAIL = [ResourceTestData("fail.txt", "")]


def test_parse_fail(test_app_data_dir: Path, logger: Logger):
    output_path = test_app_data_dir / "lines" / PARSER.__class__.__qualname__
    for fail_data in TEST_FAIL:
        with pytest.raises(ParseException):
            process_lines(
                package=__package__,
                data=fail_data,
                path_out=output_path,
                parser=PARSER,
                model=MODEL,
                serialize_only=True,
            )


def test_lines(test_app_data_dir: Path, logger: Logger):
    output_path = test_app_data_dir / "lines" / PARSER.__class__.__qualname__
    for data in TEST_DATA:
        process_lines(
            package=__package__,
            data=data,
            path_out=output_path,
            parser=PARSER,
            model=MODEL,
            serialize_only=SERIALIZE_ONLY,
        )
    assert not SERIALIZE_ONLY
