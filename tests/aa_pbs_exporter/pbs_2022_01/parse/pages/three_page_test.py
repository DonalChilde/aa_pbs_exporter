# from pathlib import Path

# from tests.aa_pbs_exporter.resources.helpers import ParseTestData, parse_pages

# from aa_pbs_exporter.pbs_2022_01.models.raw import (
#     BaseEquipment,
#     BidPackage,
#     DutyPeriod,
#     DutyPeriodRelease,
#     DutyPeriodReport,
#     Flight,
#     Hotel,
#     IndexedString,
#     Layover,
#     Page,
#     PageFooter,
#     PageHeader1,
#     PageHeader2,
#     Transportation,
#     Trip,
#     TripFooter,
#     TripHeader,
# )

# test_data = ParseTestData(
#     name="three_pages",
#     txt="""   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/
# DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# MIA 777

# SEQ 952     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −− −− −− −−
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                    9 10 −− −− −− −− −−
# 1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− −− −− −− −− −− −−
#                                  RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− −− −− −− −− −− −−
# TTL                                              3.08   2.52   6.00         9.52       −− −− −−
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 953     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −− −− −− −−
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                   −− −− −− 12 13 −− −−
# 1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− −− −− −− −− −− −−
#                                  RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− −− −− −− −− −− −−
# TTL                                              3.08   2.52   6.00         9.52       −− −− −−
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 954     3 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −− −− −− −−
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                   −− −− −− −− −− −− −−
# 1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− 17 18 −− −− 21 −−
#                                  RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− −− −− −− −− −− −−
# TTL                                              3.08   2.52   6.00         9.52       −− −− −−
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 955     5 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −− −− −− −−
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08                                  −− −− −− −− −− −− −−
#                                  RLS 1238/1338   3.08   0.00   3.08   4.38        4.08 −− −− −− −− −− −− 22
#                 DFW COURTYARD BLACKSTONE FTW                18178858700    28.52       23 −− 25 26 −− 28 −−
#                     SKYHOP GLOBAL                           9544000412                 −− −− −−
#                 RPT 1730/1830
# 2  2/2 83 1536  DFW 1830/1930  D MIA 2215/2215   2.45
#                                  RLS 2245/2245   2.45   0.00   2.45   4.15        3.45
# TTL                                              5.53   4.54  10.47        37.45
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 956     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −− −− −− −−
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                   −− −− −− −− −− −− −−
# 1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− −− −− −− −− −− −−
#                                  RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− 24 −− −− −− −− 29
# TTL                                              3.08   2.52   6.00         9.52       −− −− −−
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 957     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −− −− −− −−
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08                                  −− −− −− −− −− −− −−
#                                  RLS 1238/1338   3.08   0.00   3.08   4.38        4.08 −− −− −− −− −− −− −−
#                 DFW COURTYARD BLACKSTONE FTW                18178858700    28.52       −− −− −− −− −− −− −−
#                     SKYHOP GLOBAL                           9544000412                 30 −−  1
#                 RPT 1730/1830
# 2  2/2 83 1536  DFW 1830/1930  D MIA 2215/2215   2.45
#                                  RLS 2245/2245   2.45   0.00   2.45   4.15        3.45
# TTL                                              5.53   4.54  10.47        37.45
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 958     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1015/1015                                                          −− −− −− −− −− −− −−
# 1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− −− −− −− −− −− −−
#                                  RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− 21 22
#                 LAX THE AYRES                               13105360400    16.37       −− −− −− −− −− −− −−
#                     SKYHOP GLOBAL                           9544000412                 −− −− −−
#                 RPT 0700/1000
# 2  2/2 83  459  LAX 0800/1100  B DFW 1256/1356   2.56          1.34X
# 2  2/2 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52
#                                  RLS 1852/1852   2.56   2.52   5.48   8.52        3.56
# TTL                                              8.34   2.52  11.26        32.37
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 959     5 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1015/1015                                                          −− −− −− −− −− −− −−
# 1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− −− −− −− −− −− −−
#                                  RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− −− −−
#                 LAX THE AYRES                               13105360400    16.37       −− 24 25 −− 27 −− 29
#                     SKYHOP GLOBAL                           9544000412                 30 −− −−
#                 RPT 0700/1000
# 2  2/2 83  459  LAX 0800/1100  B DFW 1256/1356   2.56          1.34X
# 2  2/2 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52
#                                  RLS 1852/1852   2.56   2.52   5.48   8.52        3.56
# TTL                                              8.34   2.52  11.26        32.37
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−

# COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               MIA 777  INTL                             PAGE  1419
#    DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/
# DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 30107   1 OPS   POSN CA FO                HEBREW OPERATION                         Replaces prior month
#                 RPT 2140/2140                                                          sequence 932/01MAY
# 1  1/2 83   52  MIA 2240/2240  L TLV 1800/1100  12.20
#                                  RLS 1830/1130  12.20   0.00  12.20  13.50       13.20
#                 TLV TEL AVIV HILTON                         97235202222    29.20
#                     BON TOUR                                97239754200
#                 RPT 2350/1650
# 2  4/4 83  145  TLV 0050/1750  L JFK 0605/0605  12.15
#                                  RLS 0635/0635  12.15   0.00  12.15  13.45       13.15
#                 JFK COURTYARD CENTRAL PARK                  2123243773     22.55
#                     DESERT COACH                            6022866161
#                 RPT 0530/0530
# 3  5/5 25  376D JFK 0600/0600    MIA 0911/0911    AA    3.11
#                                  RLS 0941/0941   0.00   3.11   3.11   4.11        0.00
# TTL                                             24.35   3.11  27.46        84.01
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 30113   1 OPS   POSN CA FO                FRENCH   OPERATION                       Replaces prior month
#                 RPT 1633/1633                                                          sequence 910/01MAY
# 1  1/1 83 2174  MIA 1733/1733  D JFK 2028/2028   2.55
#                                  RLS 2058/2058   2.55   0.00   2.55   4.25        3.55
#                 JFK HOTEL INFO IN CCI/CREW PORTAL                          19.37
#                     TRANS INFO IN CCI/CREW PORTAL
#                 RPT 1635/1635
# 2  2/3 83   44  JFK 1735/1735  D CDG 0655/0055   7.20
#                                  RLS 0725/0125   7.20   0.00   7.20   8.50        8.20
#                 CDG PULLMAN PARIS TOUR EIFFEL               33144385600    27.50
#                     LE TRANSPORT EVENEMENTIEL               33665135886
#                 RPT 1115/0515
# 3  4/4 83   45  CDG 1215/0615  L JFK 1429/1429   8.14
#                                  RLS 1459/1459   8.14   0.00   8.14   9.44        9.14
#                 JFK COURTYARD CENTRAL PARK                  2123243773     17.31
#                     DESERT COACH                            6022866161
#                 RPT 0830/0830
# 4  5/5 83  554D JFK 0900/0900    MIA 1209/1209    AA    3.09
#                                  RLS 1239/1239   0.00   3.09   3.09   4.09        0.00
# TTL                                             18.29   7.49  26.18        92.06
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1002    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1600/1600                                                           2 −− −− −− −− −− −−
# 1  1/1 83  446  MIA 1700/1700  D LAX 1939/2239   5.39                                  −− −− −− −− −− −− −−
#                                  RLS 2009/2309   5.39   0.00   5.39   7.09        6.39 −− −− −− −− −− −− −−
#                 LAX RENAISSANCE LONG BEACH                  5624375900     23.59       −− −− −− −− −− −− −−
#                     SKYHOP GLOBAL                           9544000412                 −− −− −−
#                 RPT 2008/2308
# 2  2/3 83  340  LAX 2108/0008  D MIA 0500/0500   4.52
#                                  RLS 0530/0530   4.52   0.00   4.52   6.22        5.52
# TTL                                             10.31   5.14  15.45        37.30
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1003    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1633/1633                                                          −− −−  4 −− −− −− −−
# 1  1/1 83 2174  MIA 1733/1733  D JFK 2028/2028   2.55                                  −− −− −− −− −− −− −−
#                                  RLS 2058/2058   2.55   0.00   2.55   4.25        3.55 −− −− −− −− −− −− −−
#                 JFK JFK CTD MARRIOTT                        17188482121    11.02       −− −− −− −− −− −− −−
#                     SHUTTLE                                                            −− −− −−
#                 RPT 0800/0800
# 2  2/2 83  554  JFK 0900/0900    MIA 1209/1209   3.09
#                                  RLS 1239/1239   3.09   0.00   3.09   4.39        4.09
# TTL                                              6.04   4.26  10.30        20.06
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1004    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1020/1020                                                          −− −− −−  5 −− −− −−
# 1  1/1 83 2870  MIA 1120/1120  L CLT 1327/1327   2.07                                  −− −− −− −− −− −− −−
#                                  RLS 1357/1357   2.07   0.00   2.07   3.37        3.07 −− −− −− −− −− −− −−
#                 CLT DOUBLETREE DOWNTOWN                     17043470070    22.58       −− −− −− −− −− −− −−
#                     EXECUTIVE CAR                           7045252191                 −− −− −−
#                 RPT 1255/1255
# 2  2/2 63  553D CLT 1325/1325    DFW 1519/1619    AA    2.54   3.11X
# 2  2/2 83 1536  DFW 1830/1930    MIA 2215/2215   2.45
#                                  RLS 2245/2245   2.45   2.54   5.39   9.50        9.20
# TTL                                              4.52   5.38  10.30        36.25
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−

# COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               MIA 777  INTL                             PAGE  1422

#    DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/
# DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1005    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1115/1115                                                          −− −− −−  5 −− −− −−
# 1  1/1 83  435  MIA 1215/1215  L CLT 1432/1432   2.17          2.17X                   −− −− −− −− −− −− −−
# 1  1/1 45 2358D CLT 1649/1649    MIA 1850/1850    AA    2.01                           −− −− −− −− −− −− −−
#                                  RLS 1920/1920   2.17   2.01   4.18   8.05        3.17 −− −− −− −− −− −− −−
# TTL                                              2.17   2.58   5.15         8.05       −− −− −−
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1006    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −−  6 −− −−
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08                                  −− −− −− −− −− −− −−
#                                  RLS 1238/1338   3.08   0.00   3.08   4.38        4.08 −− −− −− −− −− −− −−
#                 DFW COURTYARD BLACKSTONE FTW                18178858700    27.22       −− −− −− −− −− −− −−
#                     SKYHOP GLOBAL                           9544000412                 −− −− −−
#                 RPT 1600/1700
# 2  2/2 83 1536  DFW 1700/1800  D MIA 2049/2049   2.49
#                                  RLS 2119/2119   2.49   0.00   2.49   4.19        3.49
# TTL                                              5.57   4.33  10.30        36.19
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1007    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −− −−  7 −−
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                   −− −− −− −− −− −− −−
# 1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− −− −− −− −− −− −−
#                                  RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− −− −− −− −− −− −−
# TTL                                              3.08   2.52   6.00         9.52       −− −− −−
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1008    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1015/1015                                                          −− −− −− −− −−  7 −−
# 1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− −− −− −− −− −− −−
#                                  RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− −− −−
#                 LAX THE AYRES                               13105360400    16.37       −− −− −− −− −− −− −−
#                     SKYHOP GLOBAL                           9544000412                 −− −− −−
#                 RPT 0700/1000
# 2  2/2 83  459  LAX 0800/1100  B DFW 1256/1356   2.56          1.34X
# 2  2/2 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52
#                                  RLS 1852/1852   2.56   2.52   5.48   8.52        3.56
# TTL                                              8.34   2.52  11.26        32.37
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1009    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 0900/0900                                                          −− −− −− −− −− −−  8
# 1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08                                  −− −− −− −− −− −− −−
#                                  RLS 1238/1338   3.08   0.00   3.08   4.38        4.08 −− −− −− −− −− −− −−
#                 DFW COURTYARD BLACKSTONE FTW                18178858700    28.52       −− −− −− −− −− −− −−
#                     SKYHOP GLOBAL                           9544000412                 −− −− −−
#                 RPT 1730/1830
# 2  2/2 83 1536  DFW 1830/1930  D MIA 2215/2215   2.45
#                                  RLS 2245/2245   2.45   0.00   2.45   4.15        3.45
# TTL                                              5.53   4.54  10.47        37.45
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1010    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1015/1015                                                          −− −− −− −− −− −−  8
# 1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− −− −− −− −− −− −−
#                                  RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− −− −−
#                 LAX RENAISSANCE LONG BEACH                  5624375900     31.57       −− −− −− −− −− −− −−
#                     SKYHOP GLOBAL                           9544000412                 −− −− −−
#                 RPT 2220/0120
# 2  2/3 82  780  LAX 2320/0220  D MIA 0709/0709   4.49
#                                  RLS 0739/0739   4.49   0.00   4.49   6.19        5.49
# TTL                                             10.27   5.18  15.45        45.24
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# SEQ 1011    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU
#                 RPT 1015/1015                                                          −− −− −− −− −− −− −−
# 1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− 10 −− −− −− −− −−
#                                  RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− −− −−
#                 LAX THE AYRES                               13105360400    16.37       −− −− −− −− −− −− −−
#                     SKYHOP GLOBAL                           9544000412                 −− −− −−
#                 RPT 0700/1000
# 2  2/2 83  459  LAX 0800/1100  B DFW 1256/1356   2.56          1.34X
# 2  2/2 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52
#                                  RLS 1852/1852   2.56   2.52   5.48   8.52        3.56
# TTL                                              8.34   2.52  11.26        32.37
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−

# COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               MIA 777  INTL                             PAGE  1423""",
#     description="A base equipment with no satellite base",
# )

# result_data = BidPackage(
#     source="three_pages",
#     pages=[
#         Page(
#             page_header_1=PageHeader1(
#                 source=IndexedString(
#                     idx=0,
#                     txt="\x0c   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/\n",
#                 )
#             ),
#             page_header_2=PageHeader2(
#                 source=IndexedString(
#                     idx=1,
#                     txt="DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01\n",
#                 ),
#                 from_date="05/02",
#                 to_date="06/01",
#             ),
#             base_equipment=BaseEquipment(
#                 source=IndexedString(idx=3, txt="MIA 777\n"),
#                 base="MIA",
#                 satellite_base="",
#                 equipment="777",
#             ),
#             page_footer=PageFooter(
#                 source=IndexedString(
#                     idx=80,
#                     txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               MIA 777  INTL                             PAGE  1419\n",
#                 ),
#                 issued="08APR2022",
#                 effective="02MAY2022",
#                 base="MIA",
#                 satelite_base="",
#                 equipment="777",
#                 division="INTL",
#                 page="1419",
#             ),
#             trips=[
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=5,
#                             txt="SEQ 952     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="952",
#                         ops_count="2",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=6,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=7,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                    9 10 −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="2.22",
#                                     equipment_change="X",
#                                     calendar="9 10 −− −− −− −− −−",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=8,
#                                         txt="1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=9,
#                                     txt="                                 RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="3.08",
#                                 synth="2.52",
#                                 total_pay="6.00",
#                                 duty="9.52",
#                                 flight_duty="4.08",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=None,
#                         )
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=10,
#                             txt="TTL                                              3.08   2.52   6.00         9.52       −− −− −−\n",
#                         ),
#                         block="3.08",
#                         synth="2.52",
#                         total_pay="6.00",
#                         tafb="9.52",
#                         calendar="−− −− −−",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=12,
#                             txt="SEQ 953     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="953",
#                         ops_count="2",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=13,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=14,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                   −− −− −− 12 13 −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="2.22",
#                                     equipment_change="X",
#                                     calendar="−− −− −− 12 13 −− −−",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=15,
#                                         txt="1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=16,
#                                     txt="                                 RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="3.08",
#                                 synth="2.52",
#                                 total_pay="6.00",
#                                 duty="9.52",
#                                 flight_duty="4.08",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=None,
#                         )
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=17,
#                             txt="TTL                                              3.08   2.52   6.00         9.52       −− −− −−\n",
#                         ),
#                         block="3.08",
#                         synth="2.52",
#                         total_pay="6.00",
#                         tafb="9.52",
#                         calendar="−− −− −−",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=19,
#                             txt="SEQ 954     3 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="954",
#                         ops_count="3",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=20,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=21,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                   −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="2.22",
#                                     equipment_change="X",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=22,
#                                         txt="1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− 17 18 −− −− 21 −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− 17 18 −− −− 21 −−",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=23,
#                                     txt="                                 RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="3.08",
#                                 synth="2.52",
#                                 total_pay="6.00",
#                                 duty="9.52",
#                                 flight_duty="4.08",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=None,
#                         )
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=24,
#                             txt="TTL                                              3.08   2.52   6.00         9.52       −− −− −−\n",
#                         ),
#                         block="3.08",
#                         synth="2.52",
#                         total_pay="6.00",
#                         tafb="9.52",
#                         calendar="−− −− −−",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=26,
#                             txt="SEQ 955     5 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="955",
#                         ops_count="5",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=27,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=28,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=29,
#                                     txt="                                 RLS 1238/1338   3.08   0.00   3.08   4.38        4.08 −− −− −− −− −− −− 22\n",
#                                 ),
#                                 release="1238/1338",
#                                 block="3.08",
#                                 synth="0.00",
#                                 total_pay="3.08",
#                                 duty="4.38",
#                                 flight_duty="4.08",
#                                 calendar="−− −− −− −− −− −− 22",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=30,
#                                         txt="                DFW COURTYARD BLACKSTONE FTW                18178858700    28.52       23 −− 25 26 −− 28 −−\n",
#                                     ),
#                                     layover_city="DFW",
#                                     name="COURTYARD BLACKSTONE FTW",
#                                     phone="18178858700",
#                                     rest="28.52",
#                                     calendar="23 −− 25 26 −− 28 −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=31,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 −− −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=32, txt="                RPT 1730/1830\n"
#                                 ),
#                                 report="1730/1830",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=33,
#                                         txt="2  2/2 83 1536  DFW 1830/1930  D MIA 2215/2215   2.45\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="1536",
#                                     deadhead="",
#                                     departure_station="DFW",
#                                     departure_time="1830/1930",
#                                     meal="D",
#                                     arrival_station="MIA",
#                                     arrival_time="2215/2215",
#                                     block="2.45",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=34,
#                                     txt="                                 RLS 2245/2245   2.45   0.00   2.45   4.15        3.45\n",
#                                 ),
#                                 release="2245/2245",
#                                 block="2.45",
#                                 synth="0.00",
#                                 total_pay="2.45",
#                                 duty="4.15",
#                                 flight_duty="3.45",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=35,
#                             txt="TTL                                              5.53   4.54  10.47        37.45\n",
#                         ),
#                         block="5.53",
#                         synth="4.54",
#                         total_pay="10.47",
#                         tafb="37.45",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=37,
#                             txt="SEQ 956     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="956",
#                         ops_count="2",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=38,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=39,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                   −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="2.22",
#                                     equipment_change="X",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=40,
#                                         txt="1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=41,
#                                     txt="                                 RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− 24 −− −− −− −− 29\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="3.08",
#                                 synth="2.52",
#                                 total_pay="6.00",
#                                 duty="9.52",
#                                 flight_duty="4.08",
#                                 calendar="−− 24 −− −− −− −− 29",
#                             ),
#                             layover=None,
#                         )
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=42,
#                             txt="TTL                                              3.08   2.52   6.00         9.52       −− −− −−\n",
#                         ),
#                         block="3.08",
#                         synth="2.52",
#                         total_pay="6.00",
#                         tafb="9.52",
#                         calendar="−− −− −−",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=44,
#                             txt="SEQ 957     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="957",
#                         ops_count="2",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=45,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=46,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=47,
#                                     txt="                                 RLS 1238/1338   3.08   0.00   3.08   4.38        4.08 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1238/1338",
#                                 block="3.08",
#                                 synth="0.00",
#                                 total_pay="3.08",
#                                 duty="4.38",
#                                 flight_duty="4.08",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=48,
#                                         txt="                DFW COURTYARD BLACKSTONE FTW                18178858700    28.52       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="DFW",
#                                     name="COURTYARD BLACKSTONE FTW",
#                                     phone="18178858700",
#                                     rest="28.52",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=49,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 30 −−  1\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="30 −− 1",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=50, txt="                RPT 1730/1830\n"
#                                 ),
#                                 report="1730/1830",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=51,
#                                         txt="2  2/2 83 1536  DFW 1830/1930  D MIA 2215/2215   2.45\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="1536",
#                                     deadhead="",
#                                     departure_station="DFW",
#                                     departure_time="1830/1930",
#                                     meal="D",
#                                     arrival_station="MIA",
#                                     arrival_time="2215/2215",
#                                     block="2.45",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=52,
#                                     txt="                                 RLS 2245/2245   2.45   0.00   2.45   4.15        3.45\n",
#                                 ),
#                                 release="2245/2245",
#                                 block="2.45",
#                                 synth="0.00",
#                                 total_pay="2.45",
#                                 duty="4.15",
#                                 flight_duty="3.45",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=53,
#                             txt="TTL                                              5.53   4.54  10.47        37.45\n",
#                         ),
#                         block="5.53",
#                         synth="4.54",
#                         total_pay="10.47",
#                         tafb="37.45",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=55,
#                             txt="SEQ 958     2 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="958",
#                         ops_count="2",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=56,
#                                     txt="                RPT 1015/1015                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="1015/1015",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=57,
#                                         txt="1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="82",
#                                     flight_number="1606",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1115/1115",
#                                     meal="L",
#                                     arrival_station="LAX",
#                                     arrival_time="1353/1653",
#                                     block="5.38",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=58,
#                                     txt="                                 RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− 21 22\n",
#                                 ),
#                                 release="1423/1723",
#                                 block="5.38",
#                                 synth="0.00",
#                                 total_pay="5.38",
#                                 duty="7.08",
#                                 flight_duty="6.38",
#                                 calendar="−− −− −− −− −− 21 22",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=59,
#                                         txt="                LAX THE AYRES                               13105360400    16.37       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="LAX",
#                                     name="THE AYRES",
#                                     phone="13105360400",
#                                     rest="16.37",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=60,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 −− −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=61, txt="                RPT 0700/1000\n"
#                                 ),
#                                 report="0700/1000",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=62,
#                                         txt="2  2/2 83  459  LAX 0800/1100  B DFW 1256/1356   2.56          1.34X\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="459",
#                                     deadhead="",
#                                     departure_station="LAX",
#                                     departure_time="0800/1100",
#                                     meal="B",
#                                     arrival_station="DFW",
#                                     arrival_time="1256/1356",
#                                     block="2.56",
#                                     synth="0.00",
#                                     ground="1.34",
#                                     equipment_change="X",
#                                     calendar="",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=63,
#                                         txt="2  2/2 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=64,
#                                     txt="                                 RLS 1852/1852   2.56   2.52   5.48   8.52        3.56\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="2.56",
#                                 synth="2.52",
#                                 total_pay="5.48",
#                                 duty="8.52",
#                                 flight_duty="3.56",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=65,
#                             txt="TTL                                              8.34   2.52  11.26        32.37\n",
#                         ),
#                         block="8.34",
#                         synth="2.52",
#                         total_pay="11.26",
#                         tafb="32.37",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=67,
#                             txt="SEQ 959     5 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="959",
#                         ops_count="5",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=68,
#                                     txt="                RPT 1015/1015                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="1015/1015",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=69,
#                                         txt="1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="82",
#                                     flight_number="1606",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1115/1115",
#                                     meal="L",
#                                     arrival_station="LAX",
#                                     arrival_time="1353/1653",
#                                     block="5.38",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=70,
#                                     txt="                                 RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1423/1723",
#                                 block="5.38",
#                                 synth="0.00",
#                                 total_pay="5.38",
#                                 duty="7.08",
#                                 flight_duty="6.38",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=71,
#                                         txt="                LAX THE AYRES                               13105360400    16.37       −− 24 25 −− 27 −− 29\n",
#                                     ),
#                                     layover_city="LAX",
#                                     name="THE AYRES",
#                                     phone="13105360400",
#                                     rest="16.37",
#                                     calendar="−− 24 25 −− 27 −− 29",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=72,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 30 −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="30 −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=73, txt="                RPT 0700/1000\n"
#                                 ),
#                                 report="0700/1000",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=74,
#                                         txt="2  2/2 83  459  LAX 0800/1100  B DFW 1256/1356   2.56          1.34X\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="459",
#                                     deadhead="",
#                                     departure_station="LAX",
#                                     departure_time="0800/1100",
#                                     meal="B",
#                                     arrival_station="DFW",
#                                     arrival_time="1256/1356",
#                                     block="2.56",
#                                     synth="0.00",
#                                     ground="1.34",
#                                     equipment_change="X",
#                                     calendar="",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=75,
#                                         txt="2  2/2 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=76,
#                                     txt="                                 RLS 1852/1852   2.56   2.52   5.48   8.52        3.56\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="2.56",
#                                 synth="2.52",
#                                 total_pay="5.48",
#                                 duty="8.52",
#                                 flight_duty="3.56",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=77,
#                             txt="TTL                                              8.34   2.52  11.26        32.37\n",
#                         ),
#                         block="8.34",
#                         synth="2.52",
#                         total_pay="11.26",
#                         tafb="32.37",
#                         calendar="",
#                     ),
#                 ),
#             ],
#         ),
#         Page(
#             page_header_1=PageHeader1(
#                 source=IndexedString(
#                     idx=81,
#                     txt="\x0c   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/\n",
#                 )
#             ),
#             page_header_2=PageHeader2(
#                 source=IndexedString(
#                     idx=82,
#                     txt="DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01\n",
#                 ),
#                 from_date="05/02",
#                 to_date="06/01",
#             ),
#             base_equipment=None,
#             page_footer=PageFooter(
#                 source=IndexedString(
#                     idx=156,
#                     txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               MIA 777  INTL                             PAGE  1422\n",
#                 ),
#                 issued="08APR2022",
#                 effective="02MAY2022",
#                 base="MIA",
#                 satelite_base="",
#                 equipment="777",
#                 division="INTL",
#                 page="1422",
#             ),
#             trips=[
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=84,
#                             txt="SEQ 30107   1 OPS   POSN CA FO                HEBREW OPERATION                         Replaces prior month\n",
#                         ),
#                         number="30107",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="HEBREW",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=85,
#                                     txt="                RPT 2140/2140                                                          sequence 932/01MAY\n",
#                                 ),
#                                 report="2140/2140",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=86,
#                                         txt="1  1/2 83   52  MIA 2240/2240  L TLV 1800/1100  12.20\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/2",
#                                     eq_code="83",
#                                     flight_number="52",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="2240/2240",
#                                     meal="L",
#                                     arrival_station="TLV",
#                                     arrival_time="1800/1100",
#                                     block="12.20",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=87,
#                                     txt="                                 RLS 1830/1130  12.20   0.00  12.20  13.50       13.20\n",
#                                 ),
#                                 release="1830/1130",
#                                 block="12.20",
#                                 synth="0.00",
#                                 total_pay="12.20",
#                                 duty="13.50",
#                                 flight_duty="13.20",
#                                 calendar="",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=88,
#                                         txt="                TLV TEL AVIV HILTON                         97235202222    29.20\n",
#                                     ),
#                                     layover_city="TLV",
#                                     name="TEL AVIV HILTON",
#                                     phone="97235202222",
#                                     rest="29.20",
#                                     calendar="",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=89,
#                                         txt="                    BON TOUR                                97239754200\n",
#                                     ),
#                                     name="BON TOUR",
#                                     phone="97239754200",
#                                     calendar="",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=90, txt="                RPT 2350/1650\n"
#                                 ),
#                                 report="2350/1650",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=91,
#                                         txt="2  4/4 83  145  TLV 0050/1750  L JFK 0605/0605  12.15\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="4/4",
#                                     eq_code="83",
#                                     flight_number="145",
#                                     deadhead="",
#                                     departure_station="TLV",
#                                     departure_time="0050/1750",
#                                     meal="L",
#                                     arrival_station="JFK",
#                                     arrival_time="0605/0605",
#                                     block="12.15",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=92,
#                                     txt="                                 RLS 0635/0635  12.15   0.00  12.15  13.45       13.15\n",
#                                 ),
#                                 release="0635/0635",
#                                 block="12.15",
#                                 synth="0.00",
#                                 total_pay="12.15",
#                                 duty="13.45",
#                                 flight_duty="13.15",
#                                 calendar="",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=93,
#                                         txt="                JFK COURTYARD CENTRAL PARK                  2123243773     22.55\n",
#                                     ),
#                                     layover_city="JFK",
#                                     name="COURTYARD CENTRAL PARK",
#                                     phone="2123243773",
#                                     rest="22.55",
#                                     calendar="",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=94,
#                                         txt="                    DESERT COACH                            6022866161\n",
#                                     ),
#                                     name="DESERT COACH",
#                                     phone="6022866161",
#                                     calendar="",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=95, txt="                RPT 0530/0530\n"
#                                 ),
#                                 report="0530/0530",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=96,
#                                         txt="3  5/5 25  376D JFK 0600/0600    MIA 0911/0911    AA    3.11\n",
#                                     ),
#                                     dutyperiod_idx="3",
#                                     dep_arr_day="5/5",
#                                     eq_code="25",
#                                     flight_number="376",
#                                     deadhead="D",
#                                     departure_station="JFK",
#                                     departure_time="0600/0600",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="0911/0911",
#                                     block="0.00",
#                                     synth="3.11",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=97,
#                                     txt="                                 RLS 0941/0941   0.00   3.11   3.11   4.11        0.00\n",
#                                 ),
#                                 release="0941/0941",
#                                 block="0.00",
#                                 synth="3.11",
#                                 total_pay="3.11",
#                                 duty="4.11",
#                                 flight_duty="0.00",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=98,
#                             txt="TTL                                             24.35   3.11  27.46        84.01\n",
#                         ),
#                         block="24.35",
#                         synth="3.11",
#                         total_pay="27.46",
#                         tafb="84.01",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=100,
#                             txt="SEQ 30113   1 OPS   POSN CA FO                FRENCH   OPERATION                       Replaces prior month\n",
#                         ),
#                         number="30113",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="FRENCH",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=101,
#                                     txt="                RPT 1633/1633                                                          sequence 910/01MAY\n",
#                                 ),
#                                 report="1633/1633",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=102,
#                                         txt="1  1/1 83 2174  MIA 1733/1733  D JFK 2028/2028   2.55\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="2174",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1733/1733",
#                                     meal="D",
#                                     arrival_station="JFK",
#                                     arrival_time="2028/2028",
#                                     block="2.55",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=103,
#                                     txt="                                 RLS 2058/2058   2.55   0.00   2.55   4.25        3.55\n",
#                                 ),
#                                 release="2058/2058",
#                                 block="2.55",
#                                 synth="0.00",
#                                 total_pay="2.55",
#                                 duty="4.25",
#                                 flight_duty="3.55",
#                                 calendar="",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=104,
#                                         txt="                JFK HOTEL INFO IN CCI/CREW PORTAL                          19.37\n",
#                                     ),
#                                     layover_city="JFK",
#                                     name="HOTEL INFO IN CCI/CREW PORTAL",
#                                     phone="",
#                                     rest="19.37",
#                                     calendar="",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=105,
#                                         txt="                    TRANS INFO IN CCI/CREW PORTAL\n",
#                                     ),
#                                     name="TRANS INFO IN CCI/CREW PORTAL",
#                                     phone="",
#                                     calendar="",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=106, txt="                RPT 1635/1635\n"
#                                 ),
#                                 report="1635/1635",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=107,
#                                         txt="2  2/3 83   44  JFK 1735/1735  D CDG 0655/0055   7.20\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/3",
#                                     eq_code="83",
#                                     flight_number="44",
#                                     deadhead="",
#                                     departure_station="JFK",
#                                     departure_time="1735/1735",
#                                     meal="D",
#                                     arrival_station="CDG",
#                                     arrival_time="0655/0055",
#                                     block="7.20",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=108,
#                                     txt="                                 RLS 0725/0125   7.20   0.00   7.20   8.50        8.20\n",
#                                 ),
#                                 release="0725/0125",
#                                 block="7.20",
#                                 synth="0.00",
#                                 total_pay="7.20",
#                                 duty="8.50",
#                                 flight_duty="8.20",
#                                 calendar="",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=109,
#                                         txt="                CDG PULLMAN PARIS TOUR EIFFEL               33144385600    27.50\n",
#                                     ),
#                                     layover_city="CDG",
#                                     name="PULLMAN PARIS TOUR EIFFEL",
#                                     phone="33144385600",
#                                     rest="27.50",
#                                     calendar="",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=110,
#                                         txt="                    LE TRANSPORT EVENEMENTIEL               33665135886\n",
#                                     ),
#                                     name="LE TRANSPORT EVENEMENTIEL",
#                                     phone="33665135886",
#                                     calendar="",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=111, txt="                RPT 1115/0515\n"
#                                 ),
#                                 report="1115/0515",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=112,
#                                         txt="3  4/4 83   45  CDG 1215/0615  L JFK 1429/1429   8.14\n",
#                                     ),
#                                     dutyperiod_idx="3",
#                                     dep_arr_day="4/4",
#                                     eq_code="83",
#                                     flight_number="45",
#                                     deadhead="",
#                                     departure_station="CDG",
#                                     departure_time="1215/0615",
#                                     meal="L",
#                                     arrival_station="JFK",
#                                     arrival_time="1429/1429",
#                                     block="8.14",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=113,
#                                     txt="                                 RLS 1459/1459   8.14   0.00   8.14   9.44        9.14\n",
#                                 ),
#                                 release="1459/1459",
#                                 block="8.14",
#                                 synth="0.00",
#                                 total_pay="8.14",
#                                 duty="9.44",
#                                 flight_duty="9.14",
#                                 calendar="",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=114,
#                                         txt="                JFK COURTYARD CENTRAL PARK                  2123243773     17.31\n",
#                                     ),
#                                     layover_city="JFK",
#                                     name="COURTYARD CENTRAL PARK",
#                                     phone="2123243773",
#                                     rest="17.31",
#                                     calendar="",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=115,
#                                         txt="                    DESERT COACH                            6022866161\n",
#                                     ),
#                                     name="DESERT COACH",
#                                     phone="6022866161",
#                                     calendar="",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=116, txt="                RPT 0830/0830\n"
#                                 ),
#                                 report="0830/0830",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=117,
#                                         txt="4  5/5 83  554D JFK 0900/0900    MIA 1209/1209    AA    3.09\n",
#                                     ),
#                                     dutyperiod_idx="4",
#                                     dep_arr_day="5/5",
#                                     eq_code="83",
#                                     flight_number="554",
#                                     deadhead="D",
#                                     departure_station="JFK",
#                                     departure_time="0900/0900",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1209/1209",
#                                     block="0.00",
#                                     synth="3.09",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=118,
#                                     txt="                                 RLS 1239/1239   0.00   3.09   3.09   4.09        0.00\n",
#                                 ),
#                                 release="1239/1239",
#                                 block="0.00",
#                                 synth="3.09",
#                                 total_pay="3.09",
#                                 duty="4.09",
#                                 flight_duty="0.00",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=119,
#                             txt="TTL                                             18.29   7.49  26.18        92.06\n",
#                         ),
#                         block="18.29",
#                         synth="7.49",
#                         total_pay="26.18",
#                         tafb="92.06",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=121,
#                             txt="SEQ 1002    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1002",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=122,
#                                     txt="                RPT 1600/1600                                                           2 −− −− −− −− −− −−\n",
#                                 ),
#                                 report="1600/1600",
#                                 calendar="2 −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=123,
#                                         txt="1  1/1 83  446  MIA 1700/1700  D LAX 1939/2239   5.39                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="446",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1700/1700",
#                                     meal="D",
#                                     arrival_station="LAX",
#                                     arrival_time="1939/2239",
#                                     block="5.39",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=124,
#                                     txt="                                 RLS 2009/2309   5.39   0.00   5.39   7.09        6.39 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="2009/2309",
#                                 block="5.39",
#                                 synth="0.00",
#                                 total_pay="5.39",
#                                 duty="7.09",
#                                 flight_duty="6.39",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=125,
#                                         txt="                LAX RENAISSANCE LONG BEACH                  5624375900     23.59       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="LAX",
#                                     name="RENAISSANCE LONG BEACH",
#                                     phone="5624375900",
#                                     rest="23.59",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=126,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 −− −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=127, txt="                RPT 2008/2308\n"
#                                 ),
#                                 report="2008/2308",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=128,
#                                         txt="2  2/3 83  340  LAX 2108/0008  D MIA 0500/0500   4.52\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/3",
#                                     eq_code="83",
#                                     flight_number="340",
#                                     deadhead="",
#                                     departure_station="LAX",
#                                     departure_time="2108/0008",
#                                     meal="D",
#                                     arrival_station="MIA",
#                                     arrival_time="0500/0500",
#                                     block="4.52",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=129,
#                                     txt="                                 RLS 0530/0530   4.52   0.00   4.52   6.22        5.52\n",
#                                 ),
#                                 release="0530/0530",
#                                 block="4.52",
#                                 synth="0.00",
#                                 total_pay="4.52",
#                                 duty="6.22",
#                                 flight_duty="5.52",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=130,
#                             txt="TTL                                             10.31   5.14  15.45        37.30\n",
#                         ),
#                         block="10.31",
#                         synth="5.14",
#                         total_pay="15.45",
#                         tafb="37.30",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=132,
#                             txt="SEQ 1003    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1003",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=133,
#                                     txt="                RPT 1633/1633                                                          −− −−  4 −− −− −− −−\n",
#                                 ),
#                                 report="1633/1633",
#                                 calendar="−− −− 4 −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=134,
#                                         txt="1  1/1 83 2174  MIA 1733/1733  D JFK 2028/2028   2.55                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="2174",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1733/1733",
#                                     meal="D",
#                                     arrival_station="JFK",
#                                     arrival_time="2028/2028",
#                                     block="2.55",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=135,
#                                     txt="                                 RLS 2058/2058   2.55   0.00   2.55   4.25        3.55 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="2058/2058",
#                                 block="2.55",
#                                 synth="0.00",
#                                 total_pay="2.55",
#                                 duty="4.25",
#                                 flight_duty="3.55",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=136,
#                                         txt="                JFK JFK CTD MARRIOTT                        17188482121    11.02       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="JFK",
#                                     name="JFK CTD MARRIOTT",
#                                     phone="17188482121",
#                                     rest="11.02",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=137,
#                                         txt="                    SHUTTLE                                                            −− −− −−\n",
#                                     ),
#                                     name="SHUTTLE",
#                                     phone="",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=138, txt="                RPT 0800/0800\n"
#                                 ),
#                                 report="0800/0800",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=139,
#                                         txt="2  2/2 83  554  JFK 0900/0900    MIA 1209/1209   3.09\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="554",
#                                     deadhead="",
#                                     departure_station="JFK",
#                                     departure_time="0900/0900",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1209/1209",
#                                     block="3.09",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=140,
#                                     txt="                                 RLS 1239/1239   3.09   0.00   3.09   4.39        4.09\n",
#                                 ),
#                                 release="1239/1239",
#                                 block="3.09",
#                                 synth="0.00",
#                                 total_pay="3.09",
#                                 duty="4.39",
#                                 flight_duty="4.09",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=141,
#                             txt="TTL                                              6.04   4.26  10.30        20.06\n",
#                         ),
#                         block="6.04",
#                         synth="4.26",
#                         total_pay="10.30",
#                         tafb="20.06",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=143,
#                             txt="SEQ 1004    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1004",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=144,
#                                     txt="                RPT 1020/1020                                                          −− −− −−  5 −− −− −−\n",
#                                 ),
#                                 report="1020/1020",
#                                 calendar="−− −− −− 5 −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=145,
#                                         txt="1  1/1 83 2870  MIA 1120/1120  L CLT 1327/1327   2.07                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="2870",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1120/1120",
#                                     meal="L",
#                                     arrival_station="CLT",
#                                     arrival_time="1327/1327",
#                                     block="2.07",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=146,
#                                     txt="                                 RLS 1357/1357   2.07   0.00   2.07   3.37        3.07 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1357/1357",
#                                 block="2.07",
#                                 synth="0.00",
#                                 total_pay="2.07",
#                                 duty="3.37",
#                                 flight_duty="3.07",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=147,
#                                         txt="                CLT DOUBLETREE DOWNTOWN                     17043470070    22.58       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="CLT",
#                                     name="DOUBLETREE DOWNTOWN",
#                                     phone="17043470070",
#                                     rest="22.58",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=148,
#                                         txt="                    EXECUTIVE CAR                           7045252191                 −− −− −−\n",
#                                     ),
#                                     name="EXECUTIVE CAR",
#                                     phone="7045252191",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=149, txt="                RPT 1255/1255\n"
#                                 ),
#                                 report="1255/1255",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=150,
#                                         txt="2  2/2 63  553D CLT 1325/1325    DFW 1519/1619    AA    2.54   3.11X\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="63",
#                                     flight_number="553",
#                                     deadhead="D",
#                                     departure_station="CLT",
#                                     departure_time="1325/1325",
#                                     meal="",
#                                     arrival_station="DFW",
#                                     arrival_time="1519/1619",
#                                     block="0.00",
#                                     synth="2.54",
#                                     ground="3.11",
#                                     equipment_change="X",
#                                     calendar="",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=151,
#                                         txt="2  2/2 83 1536  DFW 1830/1930    MIA 2215/2215   2.45\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="1536",
#                                     deadhead="",
#                                     departure_station="DFW",
#                                     departure_time="1830/1930",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="2215/2215",
#                                     block="2.45",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=152,
#                                     txt="                                 RLS 2245/2245   2.45   2.54   5.39   9.50        9.20\n",
#                                 ),
#                                 release="2245/2245",
#                                 block="2.45",
#                                 synth="2.54",
#                                 total_pay="5.39",
#                                 duty="9.50",
#                                 flight_duty="9.20",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=153,
#                             txt="TTL                                              4.52   5.38  10.30        36.25\n",
#                         ),
#                         block="4.52",
#                         synth="5.38",
#                         total_pay="10.30",
#                         tafb="36.25",
#                         calendar="",
#                     ),
#                 ),
#             ],
#         ),
#         Page(
#             page_header_1=PageHeader1(
#                 source=IndexedString(
#                     idx=158,
#                     txt="\x0c   DAY          −−DEPARTURE−−    −−−ARRIVAL−−−                GRND/        REST/\n",
#                 )
#             ),
#             page_header_2=PageHeader2(
#                 source=IndexedString(
#                     idx=159,
#                     txt="DP D/A EQ FLT#  STA DLCL/DHBT ML STA ALCL/AHBT  BLOCK  SYNTH   TPAY   DUTY  TAFB   FDP CALENDAR 05/02−06/01\n",
#                 ),
#                 from_date="05/02",
#                 to_date="06/01",
#             ),
#             base_equipment=None,
#             page_footer=PageFooter(
#                 source=IndexedString(
#                     idx=233,
#                     txt="COCKPIT  ISSUED 08APR2022  EFF 02MAY2022               MIA 777  INTL                             PAGE  1423",
#                 ),
#                 issued="08APR2022",
#                 effective="02MAY2022",
#                 base="MIA",
#                 satelite_base="",
#                 equipment="777",
#                 division="INTL",
#                 page="1423",
#             ),
#             trips=[
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=161,
#                             txt="SEQ 1005    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1005",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=162,
#                                     txt="                RPT 1115/1115                                                          −− −− −−  5 −− −− −−\n",
#                                 ),
#                                 report="1115/1115",
#                                 calendar="−− −− −− 5 −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=163,
#                                         txt="1  1/1 83  435  MIA 1215/1215  L CLT 1432/1432   2.17          2.17X                   −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="435",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1215/1215",
#                                     meal="L",
#                                     arrival_station="CLT",
#                                     arrival_time="1432/1432",
#                                     block="2.17",
#                                     synth="0.00",
#                                     ground="2.17",
#                                     equipment_change="X",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=164,
#                                         txt="1  1/1 45 2358D CLT 1649/1649    MIA 1850/1850    AA    2.01                           −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="45",
#                                     flight_number="2358",
#                                     deadhead="D",
#                                     departure_station="CLT",
#                                     departure_time="1649/1649",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1850/1850",
#                                     block="0.00",
#                                     synth="2.01",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=165,
#                                     txt="                                 RLS 1920/1920   2.17   2.01   4.18   8.05        3.17 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1920/1920",
#                                 block="2.17",
#                                 synth="2.01",
#                                 total_pay="4.18",
#                                 duty="8.05",
#                                 flight_duty="3.17",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=None,
#                         )
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=166,
#                             txt="TTL                                              2.17   2.58   5.15         8.05       −− −− −−\n",
#                         ),
#                         block="2.17",
#                         synth="2.58",
#                         total_pay="5.15",
#                         tafb="8.05",
#                         calendar="−− −− −−",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=168,
#                             txt="SEQ 1006    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1006",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=169,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −−  6 −− −−\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− 6 −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=170,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=171,
#                                     txt="                                 RLS 1238/1338   3.08   0.00   3.08   4.38        4.08 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1238/1338",
#                                 block="3.08",
#                                 synth="0.00",
#                                 total_pay="3.08",
#                                 duty="4.38",
#                                 flight_duty="4.08",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=172,
#                                         txt="                DFW COURTYARD BLACKSTONE FTW                18178858700    27.22       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="DFW",
#                                     name="COURTYARD BLACKSTONE FTW",
#                                     phone="18178858700",
#                                     rest="27.22",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=173,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 −− −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=174, txt="                RPT 1600/1700\n"
#                                 ),
#                                 report="1600/1700",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=175,
#                                         txt="2  2/2 83 1536  DFW 1700/1800  D MIA 2049/2049   2.49\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="1536",
#                                     deadhead="",
#                                     departure_station="DFW",
#                                     departure_time="1700/1800",
#                                     meal="D",
#                                     arrival_station="MIA",
#                                     arrival_time="2049/2049",
#                                     block="2.49",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=176,
#                                     txt="                                 RLS 2119/2119   2.49   0.00   2.49   4.19        3.49\n",
#                                 ),
#                                 release="2119/2119",
#                                 block="2.49",
#                                 synth="0.00",
#                                 total_pay="2.49",
#                                 duty="4.19",
#                                 flight_duty="3.49",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=177,
#                             txt="TTL                                              5.57   4.33  10.30        36.19\n",
#                         ),
#                         block="5.57",
#                         synth="4.33",
#                         total_pay="10.30",
#                         tafb="36.19",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=179,
#                             txt="SEQ 1007    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1007",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=180,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −− −−  7 −−\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− −− 7 −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=181,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08          2.22X                   −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="2.22",
#                                     equipment_change="X",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=182,
#                                         txt="1  1/1 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52                           −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=183,
#                                     txt="                                 RLS 1852/1852   3.08   2.52   6.00   9.52        4.08 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="3.08",
#                                 synth="2.52",
#                                 total_pay="6.00",
#                                 duty="9.52",
#                                 flight_duty="4.08",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=None,
#                         )
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=184,
#                             txt="TTL                                              3.08   2.52   6.00         9.52       −− −− −−\n",
#                         ),
#                         block="3.08",
#                         synth="2.52",
#                         total_pay="6.00",
#                         tafb="9.52",
#                         calendar="−− −− −−",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=186,
#                             txt="SEQ 1008    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1008",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=187,
#                                     txt="                RPT 1015/1015                                                          −− −− −− −− −−  7 −−\n",
#                                 ),
#                                 report="1015/1015",
#                                 calendar="−− −− −− −− −− 7 −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=188,
#                                         txt="1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="82",
#                                     flight_number="1606",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1115/1115",
#                                     meal="L",
#                                     arrival_station="LAX",
#                                     arrival_time="1353/1653",
#                                     block="5.38",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=189,
#                                     txt="                                 RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1423/1723",
#                                 block="5.38",
#                                 synth="0.00",
#                                 total_pay="5.38",
#                                 duty="7.08",
#                                 flight_duty="6.38",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=190,
#                                         txt="                LAX THE AYRES                               13105360400    16.37       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="LAX",
#                                     name="THE AYRES",
#                                     phone="13105360400",
#                                     rest="16.37",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=191,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 −− −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=192, txt="                RPT 0700/1000\n"
#                                 ),
#                                 report="0700/1000",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=193,
#                                         txt="2  2/2 83  459  LAX 0800/1100  B DFW 1256/1356   2.56          1.34X\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="459",
#                                     deadhead="",
#                                     departure_station="LAX",
#                                     departure_time="0800/1100",
#                                     meal="B",
#                                     arrival_station="DFW",
#                                     arrival_time="1256/1356",
#                                     block="2.56",
#                                     synth="0.00",
#                                     ground="1.34",
#                                     equipment_change="X",
#                                     calendar="",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=194,
#                                         txt="2  2/2 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=195,
#                                     txt="                                 RLS 1852/1852   2.56   2.52   5.48   8.52        3.56\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="2.56",
#                                 synth="2.52",
#                                 total_pay="5.48",
#                                 duty="8.52",
#                                 flight_duty="3.56",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=196,
#                             txt="TTL                                              8.34   2.52  11.26        32.37\n",
#                         ),
#                         block="8.34",
#                         synth="2.52",
#                         total_pay="11.26",
#                         tafb="32.37",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=198,
#                             txt="SEQ 1009    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1009",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=199,
#                                     txt="                RPT 0900/0900                                                          −− −− −− −− −− −−  8\n",
#                                 ),
#                                 report="0900/0900",
#                                 calendar="−− −− −− −− −− −− 8",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=200,
#                                         txt="1  1/1 83 1744  MIA 1000/1000  L DFW 1208/1308   3.08                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="83",
#                                     flight_number="1744",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1000/1000",
#                                     meal="L",
#                                     arrival_station="DFW",
#                                     arrival_time="1208/1308",
#                                     block="3.08",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=201,
#                                     txt="                                 RLS 1238/1338   3.08   0.00   3.08   4.38        4.08 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1238/1338",
#                                 block="3.08",
#                                 synth="0.00",
#                                 total_pay="3.08",
#                                 duty="4.38",
#                                 flight_duty="4.08",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=202,
#                                         txt="                DFW COURTYARD BLACKSTONE FTW                18178858700    28.52       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="DFW",
#                                     name="COURTYARD BLACKSTONE FTW",
#                                     phone="18178858700",
#                                     rest="28.52",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=203,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 −− −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=204, txt="                RPT 1730/1830\n"
#                                 ),
#                                 report="1730/1830",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=205,
#                                         txt="2  2/2 83 1536  DFW 1830/1930  D MIA 2215/2215   2.45\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="1536",
#                                     deadhead="",
#                                     departure_station="DFW",
#                                     departure_time="1830/1930",
#                                     meal="D",
#                                     arrival_station="MIA",
#                                     arrival_time="2215/2215",
#                                     block="2.45",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=206,
#                                     txt="                                 RLS 2245/2245   2.45   0.00   2.45   4.15        3.45\n",
#                                 ),
#                                 release="2245/2245",
#                                 block="2.45",
#                                 synth="0.00",
#                                 total_pay="2.45",
#                                 duty="4.15",
#                                 flight_duty="3.45",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=207,
#                             txt="TTL                                              5.53   4.54  10.47        37.45\n",
#                         ),
#                         block="5.53",
#                         synth="4.54",
#                         total_pay="10.47",
#                         tafb="37.45",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=209,
#                             txt="SEQ 1010    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1010",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=210,
#                                     txt="                RPT 1015/1015                                                          −− −− −− −− −− −−  8\n",
#                                 ),
#                                 report="1015/1015",
#                                 calendar="−− −− −− −− −− −− 8",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=211,
#                                         txt="1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− −− −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="82",
#                                     flight_number="1606",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1115/1115",
#                                     meal="L",
#                                     arrival_station="LAX",
#                                     arrival_time="1353/1653",
#                                     block="5.38",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=212,
#                                     txt="                                 RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1423/1723",
#                                 block="5.38",
#                                 synth="0.00",
#                                 total_pay="5.38",
#                                 duty="7.08",
#                                 flight_duty="6.38",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=213,
#                                         txt="                LAX RENAISSANCE LONG BEACH                  5624375900     31.57       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="LAX",
#                                     name="RENAISSANCE LONG BEACH",
#                                     phone="5624375900",
#                                     rest="31.57",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=214,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 −− −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=215, txt="                RPT 2220/0120\n"
#                                 ),
#                                 report="2220/0120",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=216,
#                                         txt="2  2/3 82  780  LAX 2320/0220  D MIA 0709/0709   4.49\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/3",
#                                     eq_code="82",
#                                     flight_number="780",
#                                     deadhead="",
#                                     departure_station="LAX",
#                                     departure_time="2320/0220",
#                                     meal="D",
#                                     arrival_station="MIA",
#                                     arrival_time="0709/0709",
#                                     block="4.49",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=217,
#                                     txt="                                 RLS 0739/0739   4.49   0.00   4.49   6.19        5.49\n",
#                                 ),
#                                 release="0739/0739",
#                                 block="4.49",
#                                 synth="0.00",
#                                 total_pay="4.49",
#                                 duty="6.19",
#                                 flight_duty="5.49",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=218,
#                             txt="TTL                                             10.27   5.18  15.45        45.24\n",
#                         ),
#                         block="10.27",
#                         synth="5.18",
#                         total_pay="15.45",
#                         tafb="45.24",
#                         calendar="",
#                     ),
#                 ),
#                 Trip(
#                     header=TripHeader(
#                         source=IndexedString(
#                             idx=220,
#                             txt="SEQ 1011    1 OPS   POSN CA FO                                                         MO TU WE TH FR SA SU\n",
#                         ),
#                         number="1011",
#                         ops_count="1",
#                         positions="CA FO",
#                         operations="",
#                         special_qualification="",
#                         calendar="",
#                     ),
#                     dutyperiods=[
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=221,
#                                     txt="                RPT 1015/1015                                                          −− −− −− −− −− −− −−\n",
#                                 ),
#                                 report="1015/1015",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=222,
#                                         txt="1  1/1 82 1606  MIA 1115/1115  L LAX 1353/1653   5.38                                  −− 10 −− −− −− −− −−\n",
#                                     ),
#                                     dutyperiod_idx="1",
#                                     dep_arr_day="1/1",
#                                     eq_code="82",
#                                     flight_number="1606",
#                                     deadhead="",
#                                     departure_station="MIA",
#                                     departure_time="1115/1115",
#                                     meal="L",
#                                     arrival_station="LAX",
#                                     arrival_time="1353/1653",
#                                     block="5.38",
#                                     synth="0.00",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="−− 10 −− −− −− −− −−",
#                                 )
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=223,
#                                     txt="                                 RLS 1423/1723   5.38   0.00   5.38   7.08        6.38 −− −− −− −− −− −− −−\n",
#                                 ),
#                                 release="1423/1723",
#                                 block="5.38",
#                                 synth="0.00",
#                                 total_pay="5.38",
#                                 duty="7.08",
#                                 flight_duty="6.38",
#                                 calendar="−− −− −− −− −− −− −−",
#                             ),
#                             layover=Layover(
#                                 hotel=Hotel(
#                                     source=IndexedString(
#                                         idx=224,
#                                         txt="                LAX THE AYRES                               13105360400    16.37       −− −− −− −− −− −− −−\n",
#                                     ),
#                                     layover_city="LAX",
#                                     name="THE AYRES",
#                                     phone="13105360400",
#                                     rest="16.37",
#                                     calendar="−− −− −− −− −− −− −−",
#                                 ),
#                                 transportation=Transportation(
#                                     source=IndexedString(
#                                         idx=225,
#                                         txt="                    SKYHOP GLOBAL                           9544000412                 −− −− −−\n",
#                                     ),
#                                     name="SKYHOP GLOBAL",
#                                     phone="9544000412",
#                                     calendar="−− −− −−",
#                                 ),
#                                 hotel_additional=None,
#                                 transportation_additional=None,
#                             ),
#                         ),
#                         DutyPeriod(
#                             report=DutyPeriodReport(
#                                 source=IndexedString(
#                                     idx=226, txt="                RPT 0700/1000\n"
#                                 ),
#                                 report="0700/1000",
#                                 calendar="",
#                             ),
#                             flights=[
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=227,
#                                         txt="2  2/2 83  459  LAX 0800/1100  B DFW 1256/1356   2.56          1.34X\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="83",
#                                     flight_number="459",
#                                     deadhead="",
#                                     departure_station="LAX",
#                                     departure_time="0800/1100",
#                                     meal="B",
#                                     arrival_station="DFW",
#                                     arrival_time="1256/1356",
#                                     block="2.56",
#                                     synth="0.00",
#                                     ground="1.34",
#                                     equipment_change="X",
#                                     calendar="",
#                                 ),
#                                 Flight(
#                                     source=IndexedString(
#                                         idx=228,
#                                         txt="2  2/2 26  671D DFW 1430/1530    MIA 1822/1822    AA    2.52\n",
#                                     ),
#                                     dutyperiod_idx="2",
#                                     dep_arr_day="2/2",
#                                     eq_code="26",
#                                     flight_number="671",
#                                     deadhead="D",
#                                     departure_station="DFW",
#                                     departure_time="1430/1530",
#                                     meal="",
#                                     arrival_station="MIA",
#                                     arrival_time="1822/1822",
#                                     block="0.00",
#                                     synth="2.52",
#                                     ground="0.00",
#                                     equipment_change="",
#                                     calendar="",
#                                 ),
#                             ],
#                             release=DutyPeriodRelease(
#                                 source=IndexedString(
#                                     idx=229,
#                                     txt="                                 RLS 1852/1852   2.56   2.52   5.48   8.52        3.56\n",
#                                 ),
#                                 release="1852/1852",
#                                 block="2.56",
#                                 synth="2.52",
#                                 total_pay="5.48",
#                                 duty="8.52",
#                                 flight_duty="3.56",
#                                 calendar="",
#                             ),
#                             layover=None,
#                         ),
#                     ],
#                     footer=TripFooter(
#                         source=IndexedString(
#                             idx=230,
#                             txt="TTL                                              8.34   2.52  11.26        32.37\n",
#                         ),
#                         block="8.34",
#                         synth="2.52",
#                         total_pay="11.26",
#                         tafb="32.37",
#                         calendar="",
#                     ),
#                 ),
#             ],
#         ),
#     ],
# )


# def test_page(test_app_data_dir: Path):
#     output_path = test_app_data_dir / "pages"
#     parse_pages(
#         test_data=test_data,
#         bid_package=result_data,
#         output_path=output_path,
#         # skip_test=True,
#     )
