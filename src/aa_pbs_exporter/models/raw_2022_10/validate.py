from typing import Callable, List
from aa_pbs_exporter.models.raw_2022_10 import bid_package as raw
from aa_pbs_exporter.parsers.parser_2022_10.line_parser import LineParseContext

import logging

logger = logging.getLogger(__name__)


def validate_bid_package(bid_package: raw.Package, ctx: LineParseContext):
    checks: list[Callable[[raw.Trip, raw.Page, str], str]] = [
        ops_count_matches_resolved_start_date_count,
        tafb_matches_resolved_report_release,
        resolved_report_release_time_matches_parsed_duty,
        resolved_depart_arrive_time_matched_parsed_time,
        resolved_fly_matches_parsed_fly,
        resolved_depart_arrive_within_dutyperiod,
        cumulative_flights_within_dutytime,
    ]
    indent = "\n\t"
    for page in bid_package.pages:
        for trip in page.trips:
            fail_msgs: list[str] = []
            for check in checks:
                # ctx.messenger.publish_message(f"Validation... {check.__qualname__}")
                fail_msg = check(trip, page, bid_package.source)
                if fail_msg:
                    fail_msgs.append(fail_msg)
            if fail_msgs:
                logger.warning(
                    "%s failed for %r from page %s",
                    check.__qualname__,
                    trip,
                    page.internal_page(),
                )
                # pylint: disable=protected-access
                ctx.messenger.publish_message(
                    f"Trip {trip.number()} from source line {trip._line_range()} "
                    f"failed validation. See logs for details. \n"
                    f"{indent.join(fail_msgs)}"
                )


def ops_count_matches_resolved_start_date_count(
    trip: raw.Trip, page: raw.Page, source: str
) -> str:
    _ = page, source
    if (ops_count := int(trip.ops_count())) != (
        start_dates := len(trip.resolved_start_dates)
    ):
        fail_msg = f"Parsed value {ops_count=} does not match count of {start_dates=}"
        logger.warning("Validation fail %s\n%r", fail_msg, trip)
        return fail_msg
    return ""


def tafb_matches_resolved_report_release(
    trip: raw.Trip, page: raw.Page, source: str
) -> str:
    _ = page, source
    for resolved in trip.resolved_start_dates:
        trip_length = abs(
            trip.dutyperiods[-1].resolved_reports[resolved].release
            - trip.dutyperiods[0].resolved_reports[resolved].report
        )
        if trip_length != trip.tafb():
            fail_msg = (
                f"Trip tafb {trip.tafb()} does not match release - report {trip_length}"
                f"for trip start {resolved.isoformat()}"
            )
            logger.warning("Validation fail %s\n%r", fail_msg, trip)
            return fail_msg
    return ""


def resolved_report_release_time_matches_parsed_duty(
    trip: raw.Trip, page: raw.Page, source: str
) -> str:
    _ = page, source
    for resolved in trip.resolved_start_dates:
        for idx, dutyperiod in enumerate(trip.dutyperiods):
            length = abs(
                dutyperiod.resolved_reports[resolved].release
                - dutyperiod.resolved_reports[resolved].report
            )
            if length != dutyperiod.duty():
                fail_msg = (
                    f"For trip start date of {resolved.isoformat()}, calculated "
                    f"dutyperiod length of {length} does not match parsed "
                    f"{dutyperiod.duty()} for dutyperiod {idx+1}"
                )
                logger.warning("Validation fail %s\n%r", fail_msg, trip)
                return fail_msg
    return ""


def resolved_depart_arrive_time_matched_parsed_time(
    trip: raw.Trip, page: raw.Page, source: str
) -> str:
    return ""


def resolved_fly_matches_parsed_fly(trip: raw.Trip, page: raw.Page, source: str) -> str:
    return ""


def resolved_depart_arrive_within_dutyperiod(
    trip: raw.Trip, page: raw.Page, source: str
) -> str:
    return ""


def cumulative_flights_within_dutytime(
    trip: raw.Trip, page: raw.Page, source: str
) -> str:
    return ""
