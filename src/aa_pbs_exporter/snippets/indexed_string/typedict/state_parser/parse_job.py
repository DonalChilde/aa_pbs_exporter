####################################################
#                                                  #
# src/snippets/indexed_string/typedict/state_parser/parse_job.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-05-07T11:30:50-07:00            #
# Last Modified:   #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
import logging
from io import TextIOWrapper
from time import perf_counter_ns
from typing import Any, Callable, Iterable, Sequence

from aa_pbs_exporter.pbs_2022_01.helpers.elapsed import nanos_to_seconds
from aa_pbs_exporter.snippets.indexed_string.typedict.indexed_string import (
    IndexedStringDict,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_indexed_strings import (
    parse_indexed_strings,
)
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.state_parser_protocols import (
    CollectedParseResults,
    IndexedStringParserProtocol,
    ResultHandlerProtocol,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_job(
    indexed_strings: Iterable[IndexedStringDict],
    parser_lookup: Callable[[str], Sequence[IndexedStringParserProtocol]],
    result_handler: ResultHandlerProtocol,
    beginning_state: str = "start",
    ctx: dict[str, Any] | None = None,
    debug_out: bool = True,
    debug_fp: TextIOWrapper | None = None,
    job_name: str = "",
) -> CollectedParseResults:
    if debug_out:
        print(f"Beginning parse job {job_name}", file=debug_fp)
        print(f"{result_handler.collected_results!r}", file=debug_fp)
    start = perf_counter_ns()
    try:
        for parse_result in parse_indexed_strings(
            indexed_strings=indexed_strings,
            parser_lookup=parser_lookup,
            beginning_state=beginning_state,
            ctx=ctx,
        ):
            if debug_out:
                print(f"{parse_result!r}", file=debug_fp)
            result_handler.handle_result(parse_result=parse_result, ctx=ctx)
    except Exception as error:
        if debug_out:
            print(f"{error!s}", file=debug_fp)
            raise error
    end = perf_counter_ns()
    msg = f"{job_name} complete in {nanos_to_seconds(start,end)} seconds."
    if debug_out:
        print(msg, file=debug_fp)
    logger.info(msg)
    return result_handler.collected_results
