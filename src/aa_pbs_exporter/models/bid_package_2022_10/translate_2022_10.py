from datetime import datetime

from aa_pbs_exporter.models.bid_package_2022_10 import bid_package as aa
from aa_pbs_exporter.models.raw_2022_10 import bid_package as raw


def translate_package(bid_package: raw.Package, source: str) -> aa.BidPackage:

    from_date, to_date = bid_package.from_to()
    aa_trips: list[aa.Trip] = []
    for page in bid_package.pages:
        aa_trips.extend(translate_pages(page=page, source=bid_package.source))
    return aa.BidPackage(
        source=source,
        base=bid_package.base(),
        satelite_bases=bid_package.satelite_bases(),
        from_date=from_date,
        to_date=to_date,
        trips=aa_trips,
        airports=bid_package.airports,
    )


def translate_pages(page: raw.Page, source: str) -> list[aa.Trip]:
    aa_trips: list[aa.Trip] = []
    for trip in page.trips:
        for resolved_start_date in trip.resolved_start_dates:
            assert trip.footer is not None
            aa_trip = aa.Trip(
                uuid=trip.uuid(resolved_start_date=resolved_start_date),
                number=trip.number(),
                base=trip.base(page=page),
                satelite_base=trip.satelite_base(page=page),
                positions=trip.positions(),
                operations=trip.operations(),
                division=trip.division(page=page),
                equipment=trip.equipment(page=page),
                special_qualifications=trip.special_qualification(),
                block=trip.block(),
                synth=trip.synth(),
                total_pay=trip.pay(),
                tafb=trip.tafb(),
                dutyperiods=translate_dutyperiods(
                    resolved_start_date=resolved_start_date, trip=trip
                ),
                line_ref=aa.LineReference(
                    source=source,
                    from_line=trip.header.source.idx,
                    to_line=trip.footer.source.idx,
                ),
            )
            aa_trips.append(aa_trip)
    return aa_trips


def translate_dutyperiods(
    resolved_start_date: datetime,
    trip: raw.Trip,
) -> list[aa.DutyPeriod]:
    aa_dutyperiods: list[aa.DutyPeriod] = []
    for idx, dutyperiod in enumerate(trip.dutyperiods):
        aa_dutyperiod = aa.DutyPeriod(
            idx=idx,
            report=dutyperiod.resolved_reports[resolved_start_date].report,
            report_station=dutyperiod.report_station(),
            release=dutyperiod.resolved_reports[resolved_start_date].release,
            release_station=dutyperiod.release_station(),
            block=dutyperiod.block(),
            synth=dutyperiod.synth(),
            total_pay=dutyperiod.pay(),
            duty=dutyperiod.duty(),
            flight_duty=dutyperiod.flight_duty(),
            flights=translate_flights(
                resolved_start_date=resolved_start_date, dutyperiod=dutyperiod
            ),
            layover=translate_layover(layover=dutyperiod.layover),
        )
        aa_dutyperiods.append(aa_dutyperiod)
    return aa_dutyperiods


def translate_layover(layover: raw.Layover | None) -> aa.Layover | None:
    if layover is None:
        return None
    # FIXME think through empty object logic, raw.layover returns empty string when no info
    if layover.hotel_name():
        if layover.transportation_name():
            aa_transportation = aa.Transportation(
                name=layover.transportation_name(), phone=layover.transportation_phone()
            )
        else:
            aa_transportation = None
        aa_hotel = aa.Hotel(
            name=layover.hotel_name(),
            phone=layover.hotel_phone(),
            transportation=aa_transportation,
        )
    else:
        aa_hotel = None
    if layover.hotel_additional_name():
        if layover.transportation_additional_name():
            aa_add_transportation = aa.Transportation(
                name=layover.transportation_additional_name(),
                phone=layover.transportation_additional_phone(),
            )
        else:
            aa_add_transportation = None
        aa_add_hotel = aa.Hotel(
            name=layover.hotel_additional_name(),
            phone=layover.hotel_additional_phone(),
            transportation=aa_add_transportation,
        )
    else:
        aa_add_hotel = None
    aa_layover = aa.Layover(
        odl=layover.rest(),
        city=layover.city(),
        hotel=aa_hotel,
        additional_hotel=aa_add_hotel,
    )
    return aa_layover


def translate_flights(
    resolved_start_date: datetime,
    dutyperiod: raw.DutyPeriod,
) -> list[aa.Flight]:
    aa_flights: list[aa.Flight] = []
    for idx, flight in enumerate(dutyperiod.flights):
        aa_flight = aa.Flight(
            dutyperiod_index=int(flight.dp_idx()),
            idx=idx + 1,
            dep_arr_day=flight.dep_arr_day(),
            eq_code=flight.eq_code(),
            number=flight.number(),
            deadhead=flight.deadhead(),
            departure_station=flight.departure_station(),
            departure_time=flight.resolved_flights[resolved_start_date].departure,
            meal=flight.meal(),
            arrival_station=flight.arrival_station(),
            arrival_time=flight.resolved_flights[resolved_start_date].arrival,
            block=flight.block(),
            synth=flight.synth(),
            ground=flight.ground(),
            equipment_change=flight.equipment_change(),
        )
        aa_flights.append(aa_flight)
    return aa_flights
