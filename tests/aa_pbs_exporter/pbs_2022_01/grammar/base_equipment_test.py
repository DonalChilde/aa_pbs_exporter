from logging import Logger

import pytest

from aa_pbs_exporter.pbs_2022_01.parser import grammar
from tests.aa_pbs_exporter.resources.helpers_3 import GrammarTest


Items = [
    GrammarTest(
        txt="BOS 737",
        result={"base": "BOS", "equipment": "737"},
    ),
    GrammarTest(
        txt="LAX SAN 737",
        result={"base": "LAX", "satelite_base": "SAN", "equipment": "737"},
    ),
]
parser = grammar.BaseEquipment


@pytest.mark.parametrize("test_data", Items)
def test_grammar(logger: Logger, test_data: GrammarTest):
    parse_result = parser.parse_string(test_data.txt)
    result = parse_result.as_dict()
    print(f"{parse_result}")
    print(f"{result!r}")
    assert result == test_data.result
