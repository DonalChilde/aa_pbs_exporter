from io import StringIO
from pathlib import Path

from tests.aa_pbs_exporter.resources.helpers import ParseTestData

from aa_pbs_exporter.pbs_2022_01.helpers import debug_parse_raw_bidpackage
from aa_pbs_exporter.pbs_2022_01.models.raw import (
    BidPackage,
    DutyPeriod,
    DutyPeriodRelease,
    DutyPeriodReport,
    Flight,
    Hotel,
    IndexedString,
    Layover,
    Page,
    PageFooter,
    PageHeader1,
    PageHeader2,
    Transportation,
    Trip,
    TripFooter,
    TripHeader,
)
from aa_pbs_exporter.pbs_2022_01.parse_manager import ParseManager

test_data = ParseTestData(
    name="lax_777_intl",
    txt="""   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/
DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SEQ 680     3 OPS   POSN FB ONLY                                                       MO TU WE TH FR SA SU
                RPT 1450/1450                                                          −− −− −− −− −− −− −−
1  1/2 82  136  LAX 1550/1550  D LHR 1020/0220  10.30                                  −− −− −− −− −− 14 15
                                 RLS 1050/0250  10.30   0.00  10.30  12.00       11.30 16 −− −− −− −− −− −−
                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.30       −− −− −− −− −− −− −−
                    COMET CAR HIRE (CCH) LTD                442088979984               −− −− −−
                RPT 1120/0320
2  3/3 82  137  LHR 1220/0420  L LAX 1535/1535  11.15
                                 RLS 1605/1605  11.15   0.00  11.15  12.45       12.15
TTL                                             21.45   0.00  21.45        49.15
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SEQ 681    15 OPS   POSN FB ONLY                                                       MO TU WE TH FR SA SU
                RPT 1450/1450                                                          −− −− −− −− −− −− −−
1  1/2 82  136  LAX 1550/1550  D LHR 1020/0220  10.30                                  −− −− −− −− −− −− −−
                                 RLS 1050/0250  10.30   0.00  10.30  12.00       11.30 −− 17 18 19 20 21 22
                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       23 24 25 26 27 28 29
                    COMET CAR HIRE (CCH) LTD                442088979984               30 31 −−
                RPT 1050/0250
2  3/3 82  137  LHR 1150/0350  L LAX 1505/1505  11.15
                                 RLS 1535/1535  11.15   0.00  11.15  12.45       12.15
TTL                                             21.45   0.00  21.45        48.45
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SEQ 682     2 OPS   POSN FB ONLY              ITALIAN  OPERATION                       MO TU WE TH FR SA SU
                RPT 1530/1530                                                          −−  3  4 −− −− −− −−
1  1/2 80 2201D LAX 1600/1600  L JFK 0029/2129    AA    5.29                           −− −− −− −− −− −− −−
                                 RLS 0059/2159   0.00   5.29   5.29   6.29        0.00 −− −− −− −− −− −− −−
                JFK COURTYARD CENTRAL PARK                  2123243773     17.11       −− −− −− −− −− −− −−
                    DESERT COACH                            6022866161                 −− −− −−
                RPT 1810/1510
2  2/3 83  198  JFK 1910/1610  D MXP 0905/0005   7.55
                                 RLS 0935/0035   7.55   0.00   7.55   9.25        8.55
                MXP MELIA MILANO                            3902444061     24.35
                    AIR PULLMAN                             01139033125844
                RPT 1010/0110
3  4/4 83  199  MXP 1110/0210  L JFK 1359/1059   8.49
                                 RLS 1429/1129   8.49   0.00   8.49  10.19        9.49
                JFK COURTYARD CENTRAL PARK                  2123243773     19.31
                    DESERT COACH                            6022866161
                RPT 1000/0700
4  5/5 80  331D JFK 1030/0730  L LAX 1337/1337    AA    6.07
                                 RLS 1407/1407   0.00   6.07   6.07   7.07        0.00
TTL                                             16.44  11.36  28.20        94.37
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SEQ 683    25 OPS   POSN FB ONLY              ITALIAN  OPERATION                       MO TU WE TH FR SA SU
                RPT 1530/1530                                                          −− −− −−  5  6  7  8
1  1/2 80  184D LAX 1600/1600  L JFK 0031/2131    AA    5.31                            9 10 11 12 13 14 15
                                 RLS 0101/2201   0.00   5.31   5.31   6.31        0.00 16 17 18 19 20 21 22
                JFK COURTYARD CENTRAL PARK                  2123243773     17.09       23 24 25 26 27 28 29
                    DESERT COACH                            6022866161                 −− −− −−
                RPT 1810/1510
2  2/3 83  198  JFK 1910/1610  D MXP 0905/0005   7.55
                                 RLS 0935/0035   7.55   0.00   7.55   9.25        8.55
                MXP MELIA MILANO                            3902444061     24.35
                    AIR PULLMAN                             01139033125844
                RPT 1010/0110
3  4/4 83  199  MXP 1110/0210  L JFK 1359/1059   8.49
                                 RLS 1429/1129   8.49   0.00   8.49  10.19        9.49
                JFK COURTYARD CENTRAL PARK                  2123243773     19.31
                    DESERT COACH                            6022866161
                RPT 1000/0700
4  5/5 80  331D JFK 1030/0730  L LAX 1337/1337    AA    6.07
                                 RLS 1407/1407   0.00   6.07   6.07   7.07        0.00
TTL                                             16.44  11.38  28.22        94.37
−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−

COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 777  INTL                             PAGE  1143""",
    description="A base equipment with no satellite base",
)

result_data = BidPackage(
    source="lax_777_intl",
    pages=[
        Page(
            page_header_1=PageHeader1(
                source=IndexedString(
                    idx=0,
                    txt="\x0c   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/\n",
                )
            ),
            page_header_2=PageHeader2(
                source=IndexedString(
                    idx=1,
                    txt="DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01\n",
                ),
                from_date="05/02",
                to_date="06/01",
            ),
            base_equipment=None,
            page_footer=PageFooter(
                source=IndexedString(
                    idx=68,
                    txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               LAX 777  INTL                             PAGE  1143",
                ),
                issued="08APR2022",
                effective="02MAY2022",
                base="LAX",
                satelite_base="",
                equipment="777",
                division="INTL",
                page="1143",
            ),
            trips=[
                Trip(
                    header=TripHeader(
                        source=IndexedString(
                            idx=3,
                            txt="SEQ 680     3 OPS   POSN FB ONLY                                                       MO TU WE TH FR SA SU\n",
                        ),
                        number="680",
                        ops_count="3",
                        positions="FB",
                        operations="",
                        special_qualification="",
                        calendar="",
                    ),
                    dutyperiods=[
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=4,
                                    txt="                RPT 1450/1450                                                          −− −− −− −− −− −− −−\n",
                                ),
                                report="1450/1450",
                                calendar="−− −− −− −− −− −− −−",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=5,
                                        txt="1  1/2 82  136  LAX 1550/1550  D LHR 1020/0220  10.30                                  −− −− −− −− −− 14 15\n",
                                    ),
                                    dutyperiod_idx="1",
                                    dep_arr_day="1/2",
                                    eq_code="82",
                                    flight_number="136",
                                    deadhead="",
                                    departure_station="LAX",
                                    departure_time="1550/1550",
                                    meal="D",
                                    arrival_station="LHR",
                                    arrival_time="1020/0220",
                                    block="10.30",
                                    synth="0.00",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="−− −− −− −− −− 14 15",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=6,
                                    txt="                                 RLS 1050/0250  10.30   0.00  10.30  12.00       11.30 16 −− −− −− −− −− −−\n",
                                ),
                                release="1050/0250",
                                block="10.30",
                                synth="0.00",
                                total_pay="10.30",
                                duty="12.00",
                                flight_duty="11.30",
                                calendar="16 −− −− −− −− −− −−",
                            ),
                            layover=Layover(
                                hotel=Hotel(
                                    source=IndexedString(
                                        idx=7,
                                        txt="                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.30       −− −− −− −− −− −− −−\n",
                                    ),
                                    layover_city="LHR",
                                    name="PARK PLAZA WESTMINSTER BRIDGE LONDON",
                                    phone="443334006112",
                                    rest="24.30",
                                    calendar="−− −− −− −− −− −− −−",
                                ),
                                transportation=Transportation(
                                    source=IndexedString(
                                        idx=8,
                                        txt="                    COMET CAR HIRE (CCH) LTD                442088979984               −− −− −−\n",
                                    ),
                                    name="COMET CAR HIRE (CCH) LTD",
                                    phone="442088979984",
                                    calendar="−− −− −−",
                                ),
                                hotel_additional=None,
                                transportation_additional=None,
                            ),
                        ),
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=9, txt="                RPT 1120/0320\n"
                                ),
                                report="1120/0320",
                                calendar="",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=10,
                                        txt="2  3/3 82  137  LHR 1220/0420  L LAX 1535/1535  11.15\n",
                                    ),
                                    dutyperiod_idx="2",
                                    dep_arr_day="3/3",
                                    eq_code="82",
                                    flight_number="137",
                                    deadhead="",
                                    departure_station="LHR",
                                    departure_time="1220/0420",
                                    meal="L",
                                    arrival_station="LAX",
                                    arrival_time="1535/1535",
                                    block="11.15",
                                    synth="0.00",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=11,
                                    txt="                                 RLS 1605/1605  11.15   0.00  11.15  12.45       12.15\n",
                                ),
                                release="1605/1605",
                                block="11.15",
                                synth="0.00",
                                total_pay="11.15",
                                duty="12.45",
                                flight_duty="12.15",
                                calendar="",
                            ),
                            layover=None,
                        ),
                    ],
                    footer=TripFooter(
                        source=IndexedString(
                            idx=12,
                            txt="TTL                                             21.45   0.00  21.45        49.15\n",
                        ),
                        block="21.45",
                        synth="0.00",
                        total_pay="21.45",
                        tafb="49.15",
                        calendar="",
                    ),
                ),
                Trip(
                    header=TripHeader(
                        source=IndexedString(
                            idx=14,
                            txt="SEQ 681    15 OPS   POSN FB ONLY                                                       MO TU WE TH FR SA SU\n",
                        ),
                        number="681",
                        ops_count="15",
                        positions="FB",
                        operations="",
                        special_qualification="",
                        calendar="",
                    ),
                    dutyperiods=[
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=15,
                                    txt="                RPT 1450/1450                                                          −− −− −− −− −− −− −−\n",
                                ),
                                report="1450/1450",
                                calendar="−− −− −− −− −− −− −−",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=16,
                                        txt="1  1/2 82  136  LAX 1550/1550  D LHR 1020/0220  10.30                                  −− −− −− −− −− −− −−\n",
                                    ),
                                    dutyperiod_idx="1",
                                    dep_arr_day="1/2",
                                    eq_code="82",
                                    flight_number="136",
                                    deadhead="",
                                    departure_station="LAX",
                                    departure_time="1550/1550",
                                    meal="D",
                                    arrival_station="LHR",
                                    arrival_time="1020/0220",
                                    block="10.30",
                                    synth="0.00",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="−− −− −− −− −− −− −−",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=17,
                                    txt="                                 RLS 1050/0250  10.30   0.00  10.30  12.00       11.30 −− 17 18 19 20 21 22\n",
                                ),
                                release="1050/0250",
                                block="10.30",
                                synth="0.00",
                                total_pay="10.30",
                                duty="12.00",
                                flight_duty="11.30",
                                calendar="−− 17 18 19 20 21 22",
                            ),
                            layover=Layover(
                                hotel=Hotel(
                                    source=IndexedString(
                                        idx=18,
                                        txt="                LHR PARK PLAZA WESTMINSTER BRIDGE LONDON    443334006112   24.00       23 24 25 26 27 28 29\n",
                                    ),
                                    layover_city="LHR",
                                    name="PARK PLAZA WESTMINSTER BRIDGE LONDON",
                                    phone="443334006112",
                                    rest="24.00",
                                    calendar="23 24 25 26 27 28 29",
                                ),
                                transportation=Transportation(
                                    source=IndexedString(
                                        idx=19,
                                        txt="                    COMET CAR HIRE (CCH) LTD                442088979984               30 31 −−\n",
                                    ),
                                    name="COMET CAR HIRE (CCH) LTD",
                                    phone="442088979984",
                                    calendar="30 31 −−",
                                ),
                                hotel_additional=None,
                                transportation_additional=None,
                            ),
                        ),
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=20, txt="                RPT 1050/0250\n"
                                ),
                                report="1050/0250",
                                calendar="",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=21,
                                        txt="2  3/3 82  137  LHR 1150/0350  L LAX 1505/1505  11.15\n",
                                    ),
                                    dutyperiod_idx="2",
                                    dep_arr_day="3/3",
                                    eq_code="82",
                                    flight_number="137",
                                    deadhead="",
                                    departure_station="LHR",
                                    departure_time="1150/0350",
                                    meal="L",
                                    arrival_station="LAX",
                                    arrival_time="1505/1505",
                                    block="11.15",
                                    synth="0.00",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=22,
                                    txt="                                 RLS 1535/1535  11.15   0.00  11.15  12.45       12.15\n",
                                ),
                                release="1535/1535",
                                block="11.15",
                                synth="0.00",
                                total_pay="11.15",
                                duty="12.45",
                                flight_duty="12.15",
                                calendar="",
                            ),
                            layover=None,
                        ),
                    ],
                    footer=TripFooter(
                        source=IndexedString(
                            idx=23,
                            txt="TTL                                             21.45   0.00  21.45        48.45\n",
                        ),
                        block="21.45",
                        synth="0.00",
                        total_pay="21.45",
                        tafb="48.45",
                        calendar="",
                    ),
                ),
                Trip(
                    header=TripHeader(
                        source=IndexedString(
                            idx=25,
                            txt="SEQ 682     2 OPS   POSN FB ONLY              ITALIAN  OPERATION                       MO TU WE TH FR SA SU\n",
                        ),
                        number="682",
                        ops_count="2",
                        positions="FB",
                        operations="ITALIAN",
                        special_qualification="",
                        calendar="",
                    ),
                    dutyperiods=[
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=26,
                                    txt="                RPT 1530/1530                                                          −−  3  4 −− −− −− −−\n",
                                ),
                                report="1530/1530",
                                calendar="−− 3 4 −− −− −− −−",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=27,
                                        txt="1  1/2 80 2201D LAX 1600/1600  L JFK 0029/2129    AA    5.29                           −− −− −− −− −− −− −−\n",
                                    ),
                                    dutyperiod_idx="1",
                                    dep_arr_day="1/2",
                                    eq_code="80",
                                    flight_number="2201",
                                    deadhead="D",
                                    departure_station="LAX",
                                    departure_time="1600/1600",
                                    meal="L",
                                    arrival_station="JFK",
                                    arrival_time="0029/2129",
                                    block="0.00",
                                    synth="5.29",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="−− −− −− −− −− −− −−",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=28,
                                    txt="                                 RLS 0059/2159   0.00   5.29   5.29   6.29        0.00 −− −− −− −− −− −− −−\n",
                                ),
                                release="0059/2159",
                                block="0.00",
                                synth="5.29",
                                total_pay="5.29",
                                duty="6.29",
                                flight_duty="0.00",
                                calendar="−− −− −− −− −− −− −−",
                            ),
                            layover=Layover(
                                hotel=Hotel(
                                    source=IndexedString(
                                        idx=29,
                                        txt="                JFK COURTYARD CENTRAL PARK                  2123243773     17.11       −− −− −− −− −− −− −−\n",
                                    ),
                                    layover_city="JFK",
                                    name="COURTYARD CENTRAL PARK",
                                    phone="2123243773",
                                    rest="17.11",
                                    calendar="−− −− −− −− −− −− −−",
                                ),
                                transportation=Transportation(
                                    source=IndexedString(
                                        idx=30,
                                        txt="                    DESERT COACH                            6022866161                 −− −− −−\n",
                                    ),
                                    name="DESERT COACH",
                                    phone="6022866161",
                                    calendar="−− −− −−",
                                ),
                                hotel_additional=None,
                                transportation_additional=None,
                            ),
                        ),
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=31, txt="                RPT 1810/1510\n"
                                ),
                                report="1810/1510",
                                calendar="",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=32,
                                        txt="2  2/3 83  198  JFK 1910/1610  D MXP 0905/0005   7.55\n",
                                    ),
                                    dutyperiod_idx="2",
                                    dep_arr_day="2/3",
                                    eq_code="83",
                                    flight_number="198",
                                    deadhead="",
                                    departure_station="JFK",
                                    departure_time="1910/1610",
                                    meal="D",
                                    arrival_station="MXP",
                                    arrival_time="0905/0005",
                                    block="7.55",
                                    synth="0.00",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=33,
                                    txt="                                 RLS 0935/0035   7.55   0.00   7.55   9.25        8.55\n",
                                ),
                                release="0935/0035",
                                block="7.55",
                                synth="0.00",
                                total_pay="7.55",
                                duty="9.25",
                                flight_duty="8.55",
                                calendar="",
                            ),
                            layover=Layover(
                                hotel=Hotel(
                                    source=IndexedString(
                                        idx=34,
                                        txt="                MXP MELIA MILANO                            3902444061     24.35\n",
                                    ),
                                    layover_city="MXP",
                                    name="MELIA MILANO",
                                    phone="3902444061",
                                    rest="24.35",
                                    calendar="",
                                ),
                                transportation=Transportation(
                                    source=IndexedString(
                                        idx=35,
                                        txt="                    AIR PULLMAN                             01139033125844\n",
                                    ),
                                    name="AIR PULLMAN",
                                    phone="01139033125844",
                                    calendar="",
                                ),
                                hotel_additional=None,
                                transportation_additional=None,
                            ),
                        ),
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=36, txt="                RPT 1010/0110\n"
                                ),
                                report="1010/0110",
                                calendar="",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=37,
                                        txt="3  4/4 83  199  MXP 1110/0210  L JFK 1359/1059   8.49\n",
                                    ),
                                    dutyperiod_idx="3",
                                    dep_arr_day="4/4",
                                    eq_code="83",
                                    flight_number="199",
                                    deadhead="",
                                    departure_station="MXP",
                                    departure_time="1110/0210",
                                    meal="L",
                                    arrival_station="JFK",
                                    arrival_time="1359/1059",
                                    block="8.49",
                                    synth="0.00",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=38,
                                    txt="                                 RLS 1429/1129   8.49   0.00   8.49  10.19        9.49\n",
                                ),
                                release="1429/1129",
                                block="8.49",
                                synth="0.00",
                                total_pay="8.49",
                                duty="10.19",
                                flight_duty="9.49",
                                calendar="",
                            ),
                            layover=Layover(
                                hotel=Hotel(
                                    source=IndexedString(
                                        idx=39,
                                        txt="                JFK COURTYARD CENTRAL PARK                  2123243773     19.31\n",
                                    ),
                                    layover_city="JFK",
                                    name="COURTYARD CENTRAL PARK",
                                    phone="2123243773",
                                    rest="19.31",
                                    calendar="",
                                ),
                                transportation=Transportation(
                                    source=IndexedString(
                                        idx=40,
                                        txt="                    DESERT COACH                            6022866161\n",
                                    ),
                                    name="DESERT COACH",
                                    phone="6022866161",
                                    calendar="",
                                ),
                                hotel_additional=None,
                                transportation_additional=None,
                            ),
                        ),
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=41, txt="                RPT 1000/0700\n"
                                ),
                                report="1000/0700",
                                calendar="",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=42,
                                        txt="4  5/5 80  331D JFK 1030/0730  L LAX 1337/1337    AA    6.07\n",
                                    ),
                                    dutyperiod_idx="4",
                                    dep_arr_day="5/5",
                                    eq_code="80",
                                    flight_number="331",
                                    deadhead="D",
                                    departure_station="JFK",
                                    departure_time="1030/0730",
                                    meal="L",
                                    arrival_station="LAX",
                                    arrival_time="1337/1337",
                                    block="0.00",
                                    synth="6.07",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=43,
                                    txt="                                 RLS 1407/1407   0.00   6.07   6.07   7.07        0.00\n",
                                ),
                                release="1407/1407",
                                block="0.00",
                                synth="6.07",
                                total_pay="6.07",
                                duty="7.07",
                                flight_duty="0.00",
                                calendar="",
                            ),
                            layover=None,
                        ),
                    ],
                    footer=TripFooter(
                        source=IndexedString(
                            idx=44,
                            txt="TTL                                             16.44  11.36  28.20        94.37\n",
                        ),
                        block="16.44",
                        synth="11.36",
                        total_pay="28.20",
                        tafb="94.37",
                        calendar="",
                    ),
                ),
                Trip(
                    header=TripHeader(
                        source=IndexedString(
                            idx=46,
                            txt="SEQ 683    25 OPS   POSN FB ONLY              ITALIAN  OPERATION                       MO TU WE TH FR SA SU\n",
                        ),
                        number="683",
                        ops_count="25",
                        positions="FB",
                        operations="ITALIAN",
                        special_qualification="",
                        calendar="",
                    ),
                    dutyperiods=[
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=47,
                                    txt="                RPT 1530/1530                                                          −− −− −−  5  6  7  8\n",
                                ),
                                report="1530/1530",
                                calendar="−− −− −− 5 6 7 8",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=48,
                                        txt="1  1/2 80  184D LAX 1600/1600  L JFK 0031/2131    AA    5.31                            9 10 11 12 13 14 15\n",
                                    ),
                                    dutyperiod_idx="1",
                                    dep_arr_day="1/2",
                                    eq_code="80",
                                    flight_number="184",
                                    deadhead="D",
                                    departure_station="LAX",
                                    departure_time="1600/1600",
                                    meal="L",
                                    arrival_station="JFK",
                                    arrival_time="0031/2131",
                                    block="0.00",
                                    synth="5.31",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="9 10 11 12 13 14 15",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=49,
                                    txt="                                 RLS 0101/2201   0.00   5.31   5.31   6.31        0.00 16 17 18 19 20 21 22\n",
                                ),
                                release="0101/2201",
                                block="0.00",
                                synth="5.31",
                                total_pay="5.31",
                                duty="6.31",
                                flight_duty="0.00",
                                calendar="16 17 18 19 20 21 22",
                            ),
                            layover=Layover(
                                hotel=Hotel(
                                    source=IndexedString(
                                        idx=50,
                                        txt="                JFK COURTYARD CENTRAL PARK                  2123243773     17.09       23 24 25 26 27 28 29\n",
                                    ),
                                    layover_city="JFK",
                                    name="COURTYARD CENTRAL PARK",
                                    phone="2123243773",
                                    rest="17.09",
                                    calendar="23 24 25 26 27 28 29",
                                ),
                                transportation=Transportation(
                                    source=IndexedString(
                                        idx=51,
                                        txt="                    DESERT COACH                            6022866161                 −− −− −−\n",
                                    ),
                                    name="DESERT COACH",
                                    phone="6022866161",
                                    calendar="−− −− −−",
                                ),
                                hotel_additional=None,
                                transportation_additional=None,
                            ),
                        ),
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=52, txt="                RPT 1810/1510\n"
                                ),
                                report="1810/1510",
                                calendar="",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=53,
                                        txt="2  2/3 83  198  JFK 1910/1610  D MXP 0905/0005   7.55\n",
                                    ),
                                    dutyperiod_idx="2",
                                    dep_arr_day="2/3",
                                    eq_code="83",
                                    flight_number="198",
                                    deadhead="",
                                    departure_station="JFK",
                                    departure_time="1910/1610",
                                    meal="D",
                                    arrival_station="MXP",
                                    arrival_time="0905/0005",
                                    block="7.55",
                                    synth="0.00",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=54,
                                    txt="                                 RLS 0935/0035   7.55   0.00   7.55   9.25        8.55\n",
                                ),
                                release="0935/0035",
                                block="7.55",
                                synth="0.00",
                                total_pay="7.55",
                                duty="9.25",
                                flight_duty="8.55",
                                calendar="",
                            ),
                            layover=Layover(
                                hotel=Hotel(
                                    source=IndexedString(
                                        idx=55,
                                        txt="                MXP MELIA MILANO                            3902444061     24.35\n",
                                    ),
                                    layover_city="MXP",
                                    name="MELIA MILANO",
                                    phone="3902444061",
                                    rest="24.35",
                                    calendar="",
                                ),
                                transportation=Transportation(
                                    source=IndexedString(
                                        idx=56,
                                        txt="                    AIR PULLMAN                             01139033125844\n",
                                    ),
                                    name="AIR PULLMAN",
                                    phone="01139033125844",
                                    calendar="",
                                ),
                                hotel_additional=None,
                                transportation_additional=None,
                            ),
                        ),
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=57, txt="                RPT 1010/0110\n"
                                ),
                                report="1010/0110",
                                calendar="",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=58,
                                        txt="3  4/4 83  199  MXP 1110/0210  L JFK 1359/1059   8.49\n",
                                    ),
                                    dutyperiod_idx="3",
                                    dep_arr_day="4/4",
                                    eq_code="83",
                                    flight_number="199",
                                    deadhead="",
                                    departure_station="MXP",
                                    departure_time="1110/0210",
                                    meal="L",
                                    arrival_station="JFK",
                                    arrival_time="1359/1059",
                                    block="8.49",
                                    synth="0.00",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=59,
                                    txt="                                 RLS 1429/1129   8.49   0.00   8.49  10.19        9.49\n",
                                ),
                                release="1429/1129",
                                block="8.49",
                                synth="0.00",
                                total_pay="8.49",
                                duty="10.19",
                                flight_duty="9.49",
                                calendar="",
                            ),
                            layover=Layover(
                                hotel=Hotel(
                                    source=IndexedString(
                                        idx=60,
                                        txt="                JFK COURTYARD CENTRAL PARK                  2123243773     19.31\n",
                                    ),
                                    layover_city="JFK",
                                    name="COURTYARD CENTRAL PARK",
                                    phone="2123243773",
                                    rest="19.31",
                                    calendar="",
                                ),
                                transportation=Transportation(
                                    source=IndexedString(
                                        idx=61,
                                        txt="                    DESERT COACH                            6022866161\n",
                                    ),
                                    name="DESERT COACH",
                                    phone="6022866161",
                                    calendar="",
                                ),
                                hotel_additional=None,
                                transportation_additional=None,
                            ),
                        ),
                        DutyPeriod(
                            report=DutyPeriodReport(
                                source=IndexedString(
                                    idx=62, txt="                RPT 1000/0700\n"
                                ),
                                report="1000/0700",
                                calendar="",
                            ),
                            flights=[
                                Flight(
                                    source=IndexedString(
                                        idx=63,
                                        txt="4  5/5 80  331D JFK 1030/0730  L LAX 1337/1337    AA    6.07\n",
                                    ),
                                    dutyperiod_idx="4",
                                    dep_arr_day="5/5",
                                    eq_code="80",
                                    flight_number="331",
                                    deadhead="D",
                                    departure_station="JFK",
                                    departure_time="1030/0730",
                                    meal="L",
                                    arrival_station="LAX",
                                    arrival_time="1337/1337",
                                    block="0.00",
                                    synth="6.07",
                                    ground="0.00",
                                    equipment_change="",
                                    calendar="",
                                )
                            ],
                            release=DutyPeriodRelease(
                                source=IndexedString(
                                    idx=64,
                                    txt="                                 RLS 1407/1407   0.00   6.07   6.07   7.07        0.00\n",
                                ),
                                release="1407/1407",
                                block="0.00",
                                synth="6.07",
                                total_pay="6.07",
                                duty="7.07",
                                flight_duty="0.00",
                                calendar="",
                            ),
                            layover=None,
                        ),
                    ],
                    footer=TripFooter(
                        source=IndexedString(
                            idx=65,
                            txt="TTL                                             16.44  11.38  28.22        94.37\n",
                        ),
                        block="16.44",
                        synth="11.38",
                        total_pay="28.22",
                        tafb="94.37",
                        calendar="",
                    ),
                ),
            ],
        )
    ],
)


def test_page(test_app_data_dir: Path):
    test_name = "one_page"
    output_path = test_app_data_dir / "pages" / test_name
    manager = ParseManager(ctx={})
    debug_path = output_path / f"{test_name}_debug.txt"
    bid_package = debug_parse_raw_bidpackage(
        strings=StringIO(test_data.txt),
        manager=manager,
        source=test_data.name,
        debug_file_path=debug_path,
    )
    assert bid_package == result_data
