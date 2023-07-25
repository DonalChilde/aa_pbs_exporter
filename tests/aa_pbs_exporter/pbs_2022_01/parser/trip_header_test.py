from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import parsers as parsers
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from tests.aa_pbs_exporter.resources.helpers_3 import ParserTest2


Items = [
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=0,
            txt="SEQ 25064   1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "25064",
                "ops_count": "1",
                "positions": "CA FO",
                "operations": "",
                "qualifications": "",
            },
            "source": {
                "idx": 0,
                "txt": "SEQ 25064   1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=1,
            txt="SEQ 6292    1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "6292",
                "ops_count": "1",
                "positions": "CA FO",
                "operations": "SPANISH",
                "qualifications": "",
            },
            "source": {
                "idx": 1,
                "txt": "SEQ 6292    1 OPS   POSN CA FO                SPANISH OPERATION                        MO TU WE TH FR SA SU",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=2,
            txt="SEQ 16945   1 OPS   POSN CA FO                SPECIAL QUALIFICATION                    MO TU WE TH FR SA SU",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "16945",
                "ops_count": "1",
                "positions": "CA FO",
                "operations": "",
                "qualifications": "SPECIAL",
            },
            "source": {
                "idx": 2,
                "txt": "SEQ 16945   1 OPS   POSN CA FO                SPECIAL QUALIFICATION                    MO TU WE TH FR SA SU",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=3,
            txt="SEQ 25018   2 OPS   POSN CA FO                MEXICO QUALIFICATION                     MO TU WE TH FR SA SU",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "25018",
                "ops_count": "2",
                "positions": "CA FO",
                "operations": "",
                "qualifications": "MEXICO",
            },
            "source": {
                "idx": 3,
                "txt": "SEQ 25018   2 OPS   POSN CA FO                MEXICO QUALIFICATION                     MO TU WE TH FR SA SU",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=4,
            txt="SEQ 30569   1 OPS   POSN CA FO                                                         New prior month",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "30569",
                "ops_count": "1",
                "positions": "CA FO",
                "operations": "",
                "qualifications": "",
            },
            "source": {
                "idx": 4,
                "txt": "SEQ 30569   1 OPS   POSN CA FO                                                         New prior month",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=5,
            txt="SEQ 30890   1 OPS   POSN CA FO                                                         Replaces prior month",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "30890",
                "ops_count": "1",
                "positions": "CA FO",
                "operations": "",
                "qualifications": "",
            },
            "source": {
                "idx": 5,
                "txt": "SEQ 30890   1 OPS   POSN CA FO                                                         Replaces prior month",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=6,
            txt="SEQ 19448   1 OPS   POSN CA FO                ST. THOMAS OPERATION                     MO TU WE TH FR SA SU ",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "19448",
                "ops_count": "1",
                "positions": "CA FO",
                "operations": "ST. THOMAS",
                "qualifications": "",
            },
            "source": {
                "idx": 6,
                "txt": "SEQ 19448   1 OPS   POSN CA FO                ST. THOMAS OPERATION                     MO TU WE TH FR SA SU ",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=7,
            txt="SEQ 265    10 OPS   POSN FB ONLY              GERMAN   OPERATION                       MO TU WE TH FR SA SU ",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "265",
                "ops_count": "10",
                "positions": "FB",
                "operations": "GERMAN",
                "qualifications": "",
            },
            "source": {
                "idx": 7,
                "txt": "SEQ 265    10 OPS   POSN FB ONLY              GERMAN   OPERATION                       MO TU WE TH FR SA SU ",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=8,
            txt="SEQ 264     4 OPS   POSN FB ONLY                                                       MO TU WE TH FR SA SU ",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "264",
                "ops_count": "4",
                "positions": "FB",
                "operations": "",
                "qualifications": "",
            },
            "source": {
                "idx": 8,
                "txt": "SEQ 264     4 OPS   POSN FB ONLY                                                       MO TU WE TH FR SA SU ",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=9,
            txt="SEQ 657     2 OPS   POSN FO C                                                          MO TU WE TH FR SA SU ",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "657",
                "ops_count": "2",
                "positions": "FO C",
                "operations": "",
                "qualifications": "",
            },
            "source": {
                "idx": 9,
                "txt": "SEQ 657     2 OPS   POSN FO C                                                          MO TU WE TH FR SA SU ",
            },
        },
    ),
    ParserTest2(
        idx_str=IndexedStringDict(
            idx=10,
            txt="SEQ 30097   1 OPS   POSN FB ONLY              JAPANESE OPERATION                       Replaces prior month",
        ),
        result={
            "parse_ident": "TripHeader",
            "parsed_data": {
                "number": "30097",
                "ops_count": "1",
                "positions": "FB",
                "operations": "JAPANESE",
                "qualifications": "",
            },
            "source": {
                "idx": 10,
                "txt": "SEQ 30097   1 OPS   POSN FB ONLY              JAPANESE OPERATION                       Replaces prior month",
            },
        },
    ),
]
parser = parsers.TripHeader()


@pytest.mark.parametrize("test_data", Items)
def test_parser(logger: Logger, test_data: ParserTest2):
    parse_result = parser.parse(indexed_string=test_data.idx_str)
    print(f"{parse_result!r}")

    assert parse_result == test_data.result
