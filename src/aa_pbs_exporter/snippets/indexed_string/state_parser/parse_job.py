####################################################
#                                                  #
# src/snippets/indexed_string/state_parser/parse_job.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-05-07T11:30:50-07:00            #
# Last Modified: 2023-05-08T23:54:05.947625+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Iterable, TypeVar

from aa_pbs_exporter.snippets.indexed_string.indexed_string_protocol import (
    IndexedStringProtocol,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_indexed_strings import (
    parse_indexed_strings,
)
from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
    ParseManagerProtocol,
)

T = TypeVar("T")


def parse_job(
    indexed_strings: Iterable[IndexedStringProtocol],
    manager: ParseManagerProtocol[T],
) -> T | None:
    manager.result_handler().initialize(manager.ctx)
    for parse_result in parse_indexed_strings(
        indexed_strings=indexed_strings, manager=manager
    ):
        manager.result_handler().handle_result(parse_result)
    manager.result_handler().finalize(manager.ctx)
    return manager.result_handler().result_data()
