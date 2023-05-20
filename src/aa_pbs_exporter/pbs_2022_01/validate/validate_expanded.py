import logging
from datetime import timedelta

from aa_pbs_exporter.pbs_2022_01 import messages
from aa_pbs_exporter.pbs_2022_01.helpers.compare_time import compare_time
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol
from aa_pbs_exporter.snippets.messages.publisher import Publisher

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

TIME = "%H%M"


class ExpandedValidator:
    def __init__(self, msg_bus: Publisher | None = None) -> None:
        self.msg_bus = msg_bus

    def send_message(self, msg: MessageProtocol, ctx: dict | None):
        _ = ctx
        if isinstance(msg, messages.StatusMessage):
            logger.info("%s", msg)
        else:
            logger.warning("%s", msg)
        if self.msg_bus is not None:
            self.msg_bus.publish_message(msg=msg)

    def validate(
        self,
        compact_bid: compact.BidPackage,
        expanded_bid: expanded.BidPackage,
        ctx: dict | None,
    ):
        msg = messages.StatusMessage(
            f"Validating expanded bid package. source={expanded_bid.source} uuid={expanded_bid.uuid}"
        )
        self.send_message(msg, ctx)
        # TODO make this the entry for this class, see previous for example.

    def validate_bid_package(
        self,
        compact_bid: compact.BidPackage,
        expanded_bid: expanded.BidPackage,
        ctx: dict | None,
    ):
        if ctx is None:
            ctx = {}
        self.send_message(
            msg=messages.StatusMessage(
                f"Validating expanded bid package. uuid: {expanded_bid.uuid}"
            ),
            ctx=ctx,
        )
        page_lookup = {x.uuid: x for x in compact_bid.pages}
        for page in expanded_bid.pages:
            self.validate_page(page_lookup[page.uuid], page, ctx)

    def validate_page(
        self,
        compact_page: compact.Page,
        expanded_page: expanded.Page,
        ctx: dict,
    ):
        trip_lookup = {x.uuid: x for x in compact_page.trips}
        for trip in expanded_page.trips:
            self.validate_trip(trip_lookup[trip.compact_uuid], trip, ctx)

    def validate_trip(
        self,
        compact_trip: compact.Trip,
        expanded_trip: expanded.Trip,
        ctx: dict,
    ):
        ctx["Validation_trip_number"] = expanded_trip.number
        ctx["Validation_trip_start"] = expanded_trip.start
        self.check_trip_tafb(expanded_trip, ctx)
        self.check_trip_length(expanded_trip, ctx)
        self.check_trip_end(expanded_trip, ctx)
        dutyperiod_lookup = {x.uuid: x for x in compact_trip.dutyperiods}
        for dutyperiod in expanded_trip.dutyperiods:
            self.validate_dutyperiod(
                dutyperiod_lookup[dutyperiod.compact_uuid], dutyperiod, ctx
            )

    def check_trip_length(self, expanded_trip: expanded.Trip, ctx: dict):
        total = timedelta()
        for dutyperiod in expanded_trip.dutyperiods:
            duration = dutyperiod.release.utc_date - dutyperiod.report.utc_date
            total += duration
            if dutyperiod.layover is not None:
                total += dutyperiod.layover.odl
        if total != expanded_trip.tafb:
            msg = messages.ValidationMessage(
                msg=f"Calculated trip length {total} does not match "
                f"parsed trip length {expanded_trip.tafb} for trip {expanded_trip.number} "
                f"uuid: {expanded_trip.uuid} "
                f"compact_uuid: {expanded_trip.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def check_trip_tafb(self, expanded_trip: expanded.Trip, ctx: dict):
        last_release = expanded_trip.dutyperiods[-1].release.utc_date
        trip_tafb = last_release - expanded_trip.start.utc_date
        if trip_tafb != expanded_trip.tafb:
            msg = messages.ValidationMessage(
                msg=f"Calculated trip tafb {trip_tafb} does not match "
                f"parsed trip tafb {expanded_trip.tafb} for trip {expanded_trip.number} "
                f"uuid: {expanded_trip.uuid} "
                f"compact_uuid: {expanded_trip.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def check_trip_end(self, expanded_trip: expanded.Trip, ctx: dict):
        last_release = expanded_trip.dutyperiods[-1].release
        if last_release != expanded_trip.end:
            msg = messages.ValidationMessage(
                f"Computed end of trip {expanded_trip.end!r} does not match last "
                f"dutyperiod release {last_release!r} for trip {expanded_trip.number} "
                f"uuid: {expanded_trip.uuid} "
                f"compact_uuid: {expanded_trip.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_dutyperiod(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict,
    ):
        self.check_report_times(compact_dutyperiod, expanded_dutyperiod, ctx)
        self.check_release_times(compact_dutyperiod, expanded_dutyperiod, ctx)
        self.check_dutytime(compact_dutyperiod, expanded_dutyperiod, ctx)
        flight_lookup = {x.uuid: x for x in compact_dutyperiod.flights}
        for flight in expanded_dutyperiod.flights:
            self.validate_flight(flight_lookup[flight.compact_uuid], flight, ctx)

    def check_dutytime(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict,
    ):
        dutytime = (
            expanded_dutyperiod.release.utc_date - expanded_dutyperiod.report.utc_date
        )
        if dutytime != expanded_dutyperiod.duty:
            msg = messages.ValidationMessage(
                msg=f"Calculated dutytime {dutytime} does not match "
                f"parsed dutytime {expanded_dutyperiod.duty} "
                f"uuid: {expanded_dutyperiod.uuid} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def check_report_times(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict,
    ):
        report_time = expanded_dutyperiod.report.local().time()
        if not compare_time(
            report_time,
            compact_dutyperiod.report.lcl,
            ignore_tz=True,
        ):
            msg = messages.ValidationMessage(
                msg=f"Report times do not match. "
                f"compact: {compact_dutyperiod.report.lcl!r}, "
                f"expanded: {report_time!r}. "
                f"uuid: {expanded_dutyperiod.uuid} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def check_release_times(
        self,
        compact_dutyperiod: compact.DutyPeriod,
        expanded_dutyperiod: expanded.DutyPeriod,
        ctx: dict,
    ):
        release_time = expanded_dutyperiod.release.local().time()
        if not compare_time(
            release_time,
            compact_dutyperiod.release.lcl,
            ignore_tz=True,
        ):
            msg = messages.ValidationMessage(
                msg=f"Release times do not match. "
                f"compact: {compact_dutyperiod.release.lcl!r}, "
                f"expanded: {release_time!r}. "
                f"uuid: {expanded_dutyperiod.uuid} "
                f"compact_uuid: {expanded_dutyperiod.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def validate_flight(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        ctx: dict,
    ):
        self.check_departure(compact_flight, expanded_flight, ctx)
        self.check_arrival(compact_flight, expanded_flight, ctx)
        self.check_flight_time(compact_flight, expanded_flight, ctx)

    def check_departure(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        ctx: dict,
    ):
        departure_time = expanded_flight.departure.local().time()
        if not compare_time(
            departure_time,
            compact_flight.departure.lcl,
            ignore_tz=True,
        ):
            msg = messages.ValidationMessage(
                msg=f"Departure times do not match for flight {expanded_flight.number}. "
                f"compact: {compact_flight.departure.lcl!r}, "
                f"expanded: {departure_time!r}. "
                f"uuid: {expanded_flight.uuid} "
                f"compact_uuid: {expanded_flight.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def check_arrival(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        ctx: dict,
    ):
        arrival_time = expanded_flight.arrival.local().time()
        if not compare_time(
            arrival_time,
            compact_flight.arrival.lcl,
            ignore_tz=True,
        ):
            msg = messages.ValidationMessage(
                msg=f"Arrival times do not match for flight {expanded_flight.number}. "
                f"compact: {compact_flight.arrival.lcl!r}, "
                f"expanded: {arrival_time!r}. "
                f"uuid: {expanded_flight.uuid} "
                f"compact_uuid: {expanded_flight.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg=msg, ctx=ctx)

    def check_flight_time(
        self,
        compact_flight: compact.Flight,
        expanded_flight: expanded.Flight,
        ctx: dict,
    ):
        flight_time = (
            expanded_flight.arrival.utc_date - expanded_flight.departure.utc_date
        )
        if expanded_flight.deadhead:
            if flight_time != expanded_flight.synth:
                msg = messages.ValidationMessage(
                    f"Flight time {flight_time} does not match synth time "
                    f"{expanded_flight.synth} on deadhead flight {expanded_flight.number}. "
                    f"uuid: {expanded_flight.uuid} "
                    f"compact_uuid: {expanded_flight.compact_uuid} "
                    f"{ctx!r}"
                )
                self.send_message(msg, ctx)
            return
        if flight_time != expanded_flight.block:
            msg = messages.ValidationMessage(
                f"Flight time {flight_time} does not match block time "
                f"{expanded_flight.block} on flight {expanded_flight.number}. "
                f"uuid: {expanded_flight.uuid} "
                f"compact_uuid: {expanded_flight.compact_uuid} "
                f"{ctx!r}"
            )
            self.send_message(msg, ctx)

    def validate_layover(
        self,
        compact_layover: compact.Layover,
        expanded_layover: expanded.Layover,
        ctx: dict,
    ):
        pass

    def validate_hotel(
        self,
        conpact_hotel: compact.Hotel,
        expanded_hotel: expanded.Hotel,
        ctx: dict,
    ):
        pass

    def validate_transportation(
        self,
        compact_transportation: compact.Transportation,
        expanded_transportation: expanded.Transportation,
        ctx: dict,
    ):
        pass
