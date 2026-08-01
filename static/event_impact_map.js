// Ported from the standalone "Event Impact Map" D3 prototype. Logic is kept
// verbatim (DATA + prep/findBaselineIdx/computeMovements/render/control
// wiring); the only structural change is wrapping the module-load-time code
// into initEventImpactMap() instead of running it immediately, since this
// widget starts hidden as one Explore tab — running render() against a
// hidden (0-width) container would produce a zero-width treemap.

const DATA = {"events": [{"name": "9/11 Terrorist Attacks", "date": "2001-09-11"}, {"name": "U.S. Invasion of Afghanistan (Operation Enduring Freedom)", "date": "2001-10-07"}, {"name": "Enron Scandal / Collapse", "date": "2001-12-02"}, {"name": "SARS Outbreak", "date": "2002-11-16"}, {"name": "U.S. Invasion of Iraq (Operation Iraqi Freedom)", "date": "2003-03-20"}, {"name": "Hurricane Katrina", "date": "2005-08-29"}, {"name": "U.S. Housing Market Crash Begins", "date": "2007-08-01"}, {"name": "Bear Stearns Collapse", "date": "2008-03-16"}, {"name": "Global Financial Crisis / Lehman Brothers Collapse", "date": "2008-09-15"}, {"name": "TARP Bailout Passed", "date": "2008-10-03"}, {"name": "European Sovereign Debt Crisis (Greece Bailout)", "date": "2010-05-02"}, {"name": "Flash Crash", "date": "2010-05-06"}, {"name": "Arab Spring Begins", "date": "2010-12-18"}, {"name": "Libyan Civil War / Oil Supply Disruption", "date": "2011-02-15"}, {"name": "Fukushima Nuclear Disaster / Japan Earthquake", "date": "2011-03-11"}, {"name": "U.S./NATO Intervention in Libya (Operation Odyssey Dawn)", "date": "2011-03-19"}, {"name": "Killing of Osama bin Laden (Operation Neptune Spear)", "date": "2011-05-02"}, {"name": "U.S. Credit Rating Downgrade (S&P)", "date": "2011-08-05"}, {"name": "Eurozone Crisis Escalation (Greek Debt Restructuring)", "date": "2012-03-09"}, {"name": "Federal Reserve 'Taper Tantrum'", "date": "2013-05-22"}, {"name": "Russia Annexation of Crimea", "date": "2014-02-20"}, {"name": "U.S. Military Intervention Against ISIS (Operation Inherent Resolve)", "date": "2014-08-08"}, {"name": "Oil Price Collapse (OPEC Supply Glut)", "date": "2014-11-27"}, {"name": "Chinese Stock Market Crash", "date": "2015-06-12"}, {"name": "Brexit Referendum", "date": "2016-06-23"}, {"name": "U.S. Presidential Election (Trump Win)", "date": "2016-11-08"}, {"name": "U.S.-China Trade War Begins", "date": "2018-03-22"}, {"name": "U.S. Stock Market Selloff (Q4)", "date": "2018-12-01"}, {"name": "Killing of Qasem Soleimani / U.S.-Iran Tensions", "date": "2020-01-03"}, {"name": "OPEC+ Oil Price War (Saudi-Russia)", "date": "2020-03-08"}, {"name": "COVID-19 Pandemic Declared / Market Crash", "date": "2020-03-11"}, {"name": "U.S. Oil Futures Go Negative", "date": "2020-04-20"}, {"name": "COVID-19 Vaccine Rollout Begins", "date": "2020-12-14"}, {"name": "GameStop / Meme Stock Short Squeeze", "date": "2021-01-22"}, {"name": "Suez Canal Blockage (Ever Given)", "date": "2021-03-23"}, {"name": "U.S. Withdrawal from Afghanistan", "date": "2021-04-14"}, {"name": "Russia Invades Ukraine", "date": "2022-02-24"}, {"name": "Federal Reserve Aggressive Rate Hikes Begin", "date": "2022-03-16"}, {"name": "U.S. Inflation Peaks at 40-Year High", "date": "2022-06-10"}, {"name": "Silicon Valley Bank Collapse", "date": "2023-03-10"}, {"name": "Credit Suisse Collapse / Forced UBS Merger", "date": "2023-03-19"}, {"name": "OPEC+ Surprise Production Cuts", "date": "2023-04-02"}, {"name": "U.S. Debt Ceiling Crisis", "date": "2023-05-01"}, {"name": "Israel-Hamas War Begins", "date": "2023-10-07"}, {"name": "Red Sea Shipping Crisis (Houthi Attacks)", "date": "2023-11-19"}, {"name": "U.S. Airstrikes on Houthi Targets in Yemen (Operation Poseidon Archer)", "date": "2024-01-11"}, {"name": "Israel-Iran Conflict Escalation", "date": "2024-04-13"}, {"name": "Federal Reserve Begins Rate Cuts", "date": "2024-09-18"}, {"name": "U.S. Presidential Election (Trump Win)", "date": "2024-11-05"}, {"name": "DeepSeek AI Shock to Tech Stocks", "date": "2025-01-27"}, {"name": "U.S. Tariff Announcements ('Liberation Day' Tariffs)", "date": "2025-04-02"}, {"name": "U.S. Strikes on Iranian Nuclear Facilities (Operation Midnight Hammer)", "date": "2025-06-21"}], "sp500": [{"date": "1999-01-01", "value": 1248.77}, {"date": "1999-02-01", "value": 1246.58}, {"date": "1999-03-01", "value": 1281.66}, {"date": "1999-04-01", "value": 1334.76}, {"date": "1999-05-01", "value": 1332.07}, {"date": "1999-06-01", "value": 1322.55}, {"date": "1999-07-01", "value": 1380.99}, {"date": "1999-08-01", "value": 1327.49}, {"date": "1999-09-01", "value": 1318.17}, {"date": "1999-10-01", "value": 1300.01}, {"date": "1999-11-01", "value": 1391.0}, {"date": "1999-12-01", "value": 1428.68}, {"date": "2000-01-01", "value": 1425.59}, {"date": "2000-02-01", "value": 1388.87}, {"date": "2000-03-01", "value": 1442.21}, {"date": "2000-04-01", "value": 1461.36}, {"date": "2000-05-01", "value": 1418.48}, {"date": "2000-06-01", "value": 1461.96}, {"date": "2000-07-01", "value": 1473.0}, {"date": "2000-08-01", "value": 1485.46}, {"date": "2000-09-01", "value": 1468.05}, {"date": "2000-10-01", "value": 1390.14}, {"date": "2000-11-01", "value": 1378.04}, {"date": "2000-12-01", "value": 1330.93}, {"date": "2001-01-01", "value": 1335.63}, {"date": "2001-02-01", "value": 1305.75}, {"date": "2001-03-01", "value": 1185.85}, {"date": "2001-04-01", "value": 1189.84}, {"date": "2001-05-01", "value": 1270.37}, {"date": "2001-06-01", "value": 1238.71}, {"date": "2001-07-01", "value": 1204.45}, {"date": "2001-08-01", "value": 1178.5}, {"date": "2001-09-01", "value": 1044.64}, {"date": "2001-10-01", "value": 1076.59}, {"date": "2001-11-01", "value": 1129.68}, {"date": "2001-12-01", "value": 1144.93}, {"date": "2002-01-01", "value": 1140.21}, {"date": "2002-02-01", "value": 1100.67}, {"date": "2002-03-01", "value": 1153.79}, {"date": "2002-04-01", "value": 1111.93}, {"date": "2002-05-01", "value": 1079.25}, {"date": "2002-06-01", "value": 1014.02}, {"date": "2002-07-01", "value": 903.59}, {"date": "2002-08-01", "value": 912.55}, {"date": "2002-09-01", "value": 867.81}, {"date": "2002-10-01", "value": 854.63}, {"date": "2002-11-01", "value": 909.93}, {"date": "2002-12-01", "value": 899.18}, {"date": "2003-01-01", "value": 895.84}, {"date": "2003-02-01", "value": 837.03}, {"date": "2003-03-01", "value": 846.63}, {"date": "2003-04-01", "value": 890.03}, {"date": "2003-05-01", "value": 935.96}, {"date": "2003-06-01", "value": 988.0}, {"date": "2003-07-01", "value": 992.54}, {"date": "2003-08-01", "value": 989.53}, {"date": "2003-09-01", "value": 1019.44}, {"date": "2003-10-01", "value": 1038.73}, {"date": "2003-11-01", "value": 1049.9}, {"date": "2003-12-01", "value": 1080.64}, {"date": "2004-01-01", "value": 1132.52}, {"date": "2004-02-01", "value": 1143.36}, {"date": "2004-03-01", "value": 1123.98}, {"date": "2004-04-01", "value": 1133.36}, {"date": "2004-05-01", "value": 1102.78}, {"date": "2004-06-01", "value": 1132.76}, {"date": "2004-07-01", "value": 1105.85}, {"date": "2004-08-01", "value": 1088.94}, {"date": "2004-09-01", "value": 1117.66}, {"date": "2004-10-01", "value": 1117.21}, {"date": "2004-11-01", "value": 1168.94}, {"date": "2004-12-01", "value": 1199.21}, {"date": "2005-01-01", "value": 1181.41}, {"date": "2005-02-01", "value": 1199.63}, {"date": "2005-03-01", "value": 1194.9}, {"date": "2005-04-01", "value": 1164.43}, {"date": "2005-05-01", "value": 1178.28}, {"date": "2005-06-01", "value": 1202.25}, {"date": "2005-07-01", "value": 1222.24}, {"date": "2005-08-01", "value": 1224.27}, {"date": "2005-09-01", "value": 1225.92}, {"date": "2005-10-01", "value": 1191.96}, {"date": "2005-11-01", "value": 1237.37}, {"date": "2005-12-01", "value": 1262.07}, {"date": "2006-01-01", "value": 1278.73}, {"date": "2006-02-01", "value": 1276.65}, {"date": "2006-03-01", "value": 1293.74}, {"date": "2006-04-01", "value": 1302.17}, {"date": "2006-05-01", "value": 1290.01}, {"date": "2006-06-01", "value": 1253.17}, {"date": "2006-07-01", "value": 1260.24}, {"date": "2006-08-01", "value": 1287.15}, {"date": "2006-09-01", "value": 1317.74}, {"date": "2006-10-01", "value": 1363.38}, {"date": "2006-11-01", "value": 1388.64}, {"date": "2006-12-01", "value": 1416.42}, {"date": "2007-01-01", "value": 1424.16}, {"date": "2007-02-01", "value": 1444.8}, {"date": "2007-03-01", "value": 1406.95}, {"date": "2007-04-01", "value": 1463.64}, {"date": "2007-05-01", "value": 1511.14}, {"date": "2007-06-01", "value": 1514.19}, {"date": "2007-07-01", "value": 1520.71}, {"date": "2007-08-01", "value": 1454.62}, {"date": "2007-09-01", "value": 1497.12}, {"date": "2007-10-01", "value": 1539.66}, {"date": "2007-11-01", "value": 1463.39}, {"date": "2007-12-01", "value": 1479.22}, {"date": "2008-01-01", "value": 1378.76}, {"date": "2008-02-01", "value": 1354.87}, {"date": "2008-03-01", "value": 1316.94}, {"date": "2008-04-01", "value": 1370.47}, {"date": "2008-05-01", "value": 1403.22}, {"date": "2008-06-01", "value": 1341.25}, {"date": "2008-07-01", "value": 1257.33}, {"date": "2008-08-01", "value": 1281.47}, {"date": "2008-09-01", "value": 1216.95}, {"date": "2008-10-01", "value": 968.8}, {"date": "2008-11-01", "value": 883.04}, {"date": "2008-12-01", "value": 877.56}, {"date": "2009-01-01", "value": 865.58}, {"date": "2009-02-01", "value": 805.23}, {"date": "2009-03-01", "value": 757.13}, {"date": "2009-04-01", "value": 848.15}, {"date": "2009-05-01", "value": 902.41}, {"date": "2009-06-01", "value": 926.12}, {"date": "2009-07-01", "value": 935.82}, {"date": "2009-08-01", "value": 1009.73}, {"date": "2009-09-01", "value": 1044.55}, {"date": "2009-10-01", "value": 1067.66}, {"date": "2009-11-01", "value": 1088.07}, {"date": "2009-12-01", "value": 1110.38}, {"date": "2010-01-01", "value": 1123.58}, {"date": "2010-02-01", "value": 1089.16}, {"date": "2010-03-01", "value": 1152.05}, {"date": "2010-04-01", "value": 1197.32}, {"date": "2010-05-01", "value": 1125.06}, {"date": "2010-06-01", "value": 1083.36}, {"date": "2010-07-01", "value": 1079.8}, {"date": "2010-08-01", "value": 1087.28}, {"date": "2010-09-01", "value": 1122.08}, {"date": "2010-10-01", "value": 1171.58}, {"date": "2010-11-01", "value": 1198.89}, {"date": "2010-12-01", "value": 1241.53}, {"date": "2011-01-01", "value": 1282.62}, {"date": "2011-02-01", "value": 1321.12}, {"date": "2011-03-01", "value": 1304.49}, {"date": "2011-04-01", "value": 1331.51}, {"date": "2011-05-01", "value": 1338.31}, {"date": "2011-06-01", "value": 1287.29}, {"date": "2011-07-01", "value": 1325.19}, {"date": "2011-08-01", "value": 1185.31}, {"date": "2011-09-01", "value": 1173.88}, {"date": "2011-10-01", "value": 1207.22}, {"date": "2011-11-01", "value": 1226.42}, {"date": "2011-12-01", "value": 1243.32}, {"date": "2012-01-01", "value": 1300.58}, {"date": "2012-02-01", "value": 1352.49}, {"date": "2012-03-01", "value": 1389.24}, {"date": "2012-04-01", "value": 1386.43}, {"date": "2012-05-01", "value": 1341.27}, {"date": "2012-06-01", "value": 1323.48}, {"date": "2012-07-01", "value": 1359.78}, {"date": "2012-08-01", "value": 1403.45}, {"date": "2012-09-01", "value": 1443.42}, {"date": "2012-10-01", "value": 1437.82}, {"date": "2012-11-01", "value": 1394.51}, {"date": "2012-12-01", "value": 1422.29}, {"date": "2013-01-01", "value": 1480.4}, {"date": "2013-02-01", "value": 1512.31}, {"date": "2013-03-01", "value": 1550.83}, {"date": "2013-04-01", "value": 1570.7}, {"date": "2013-05-01", "value": 1639.84}, {"date": "2013-06-01", "value": 1618.77}, {"date": "2013-07-01", "value": 1668.68}, {"date": "2013-08-01", "value": 1670.09}, {"date": "2013-09-01", "value": 1687.17}, {"date": "2013-10-01", "value": 1720.03}, {"date": "2013-11-01", "value": 1783.54}, {"date": "2013-12-01", "value": 1807.78}, {"date": "2014-01-01", "value": 1822.36}, {"date": "2014-02-01", "value": 1817.04}, {"date": "2014-03-01", "value": 1863.52}, {"date": "2014-04-01", "value": 1864.26}, {"date": "2014-05-01", "value": 1889.77}, {"date": "2014-06-01", "value": 1947.09}, {"date": "2014-07-01", "value": 1973.1}, {"date": "2014-08-01", "value": 1961.53}, {"date": "2014-09-01", "value": 1993.23}, {"date": "2014-10-01", "value": 1937.27}, {"date": "2014-11-01", "value": 2044.57}, {"date": "2014-12-01", "value": 2054.27}, {"date": "2015-01-01", "value": 2028.18}, {"date": "2015-02-01", "value": 2082.2}, {"date": "2015-03-01", "value": 2079.99}, {"date": "2015-04-01", "value": 2094.86}, {"date": "2015-05-01", "value": 2111.94}, {"date": "2015-06-01", "value": 2099.29}, {"date": "2015-07-01", "value": 2094.14}, {"date": "2015-08-01", "value": 2039.87}, {"date": "2015-09-01", "value": 1944.41}, {"date": "2015-10-01", "value": 2024.81}, {"date": "2015-11-01", "value": 2080.62}, {"date": "2015-12-01", "value": 2054.08}, {"date": "2016-01-01", "value": 1918.6}, {"date": "2016-02-01", "value": 1904.42}, {"date": "2016-03-01", "value": 2021.95}, {"date": "2016-04-01", "value": 2075.54}, {"date": "2016-05-01", "value": 2065.55}, {"date": "2016-06-01", "value": 2083.89}, {"date": "2016-07-01", "value": 2148.9}, {"date": "2016-08-01", "value": 2170.95}, {"date": "2016-09-01", "value": 2157.69}, {"date": "2016-10-01", "value": 2143.02}, {"date": "2016-11-01", "value": 2164.99}, {"date": "2016-12-01", "value": 2246.63}, {"date": "2017-01-01", "value": 2275.12}, {"date": "2017-02-01", "value": 2329.91}, {"date": "2017-03-01", "value": 2366.82}, {"date": "2017-04-01", "value": 2359.31}, {"date": "2017-05-01", "value": 2395.35}, {"date": "2017-06-01", "value": 2433.99}, {"date": "2017-07-01", "value": 2454.1}, {"date": "2017-08-01", "value": 2456.22}, {"date": "2017-09-01", "value": 2492.84}, {"date": "2017-10-01", "value": 2557.0}, {"date": "2017-11-01", "value": 2593.61}, {"date": "2017-12-01", "value": 2664.34}, {"date": "2018-01-01", "value": 2789.8}, {"date": "2018-02-01", "value": 2705.16}, {"date": "2018-03-01", "value": 2702.77}, {"date": "2018-04-01", "value": 2653.63}, {"date": "2018-05-01", "value": 2701.49}, {"date": "2018-06-01", "value": 2754.35}, {"date": "2018-07-01", "value": 2793.64}, {"date": "2018-08-01", "value": 2857.82}, {"date": "2018-09-01", "value": 2901.5}, {"date": "2018-10-01", "value": 2785.46}, {"date": "2018-11-01", "value": 2723.23}, {"date": "2018-12-01", "value": 2567.31}, {"date": "2019-01-01", "value": 2607.39}, {"date": "2019-02-01", "value": 2754.86}, {"date": "2019-03-01", "value": 2803.98}, {"date": "2019-04-01", "value": 2903.8}, {"date": "2019-05-01", "value": 2854.71}, {"date": "2019-06-01", "value": 2890.17}, {"date": "2019-07-01", "value": 2996.11}, {"date": "2019-08-01", "value": 2897.5}, {"date": "2019-09-01", "value": 2982.16}, {"date": "2019-10-01", "value": 2977.68}, {"date": "2019-11-01", "value": 3104.9}, {"date": "2019-12-01", "value": 3176.75}, {"date": "2020-01-01", "value": 3278.2}, {"date": "2020-02-01", "value": 3277.31}, {"date": "2020-03-01", "value": 2652.39}, {"date": "2020-04-01", "value": 2761.98}, {"date": "2020-05-01", "value": 2919.61}, {"date": "2020-06-01", "value": 3104.66}, {"date": "2020-07-01", "value": 3207.62}, {"date": "2020-08-01", "value": 3391.71}, {"date": "2020-09-01", "value": 3365.52}, {"date": "2020-10-01", "value": 3418.7}, {"date": "2020-11-01", "value": 3548.99}, {"date": "2020-12-01", "value": 3695.31}, {"date": "2021-01-01", "value": 3793.75}, {"date": "2021-02-01", "value": 3883.43}, {"date": "2021-03-01", "value": 3910.51}, {"date": "2021-04-01", "value": 4141.18}, {"date": "2021-05-01", "value": 4167.85}, {"date": "2021-06-01", "value": 4238.49}, {"date": "2021-07-01", "value": 4363.71}, {"date": "2021-08-01", "value": 4454.21}, {"date": "2021-09-01", "value": 4445.54}, {"date": "2021-10-01", "value": 4460.71}, {"date": "2021-11-01", "value": 4667.39}, {"date": "2021-12-01", "value": 4674.77}, {"date": "2022-01-01", "value": 4573.82}, {"date": "2022-02-01", "value": 4435.98}, {"date": "2022-03-01", "value": 4391.27}, {"date": "2022-04-01", "value": 4391.3}, {"date": "2022-05-01", "value": 4040.36}, {"date": "2022-06-01", "value": 3898.95}, {"date": "2022-07-01", "value": 3911.73}, {"date": "2022-08-01", "value": 4158.56}, {"date": "2022-09-01", "value": 3850.52}, {"date": "2022-10-01", "value": 3726.05}, {"date": "2022-11-01", "value": 3917.49}, {"date": "2022-12-01", "value": 3912.38}, {"date": "2023-01-01", "value": 3960.66}, {"date": "2023-02-01", "value": 4079.68}, {"date": "2023-03-01", "value": 3968.56}, {"date": "2023-04-01", "value": 4121.47}, {"date": "2023-05-01", "value": 4146.17}, {"date": "2023-06-01", "value": 4345.37}, {"date": "2023-07-01", "value": 4508.08}, {"date": "2023-08-01", "value": 4457.36}, {"date": "2023-09-01", "value": 4515.77}, {"date": "2023-10-01", "value": 4269.4}, {"date": "2023-11-01", "value": 4460.06}, {"date": "2023-12-01", "value": 4685.05}, {"date": "2024-01-01", "value": 4804.49}, {"date": "2024-02-01", "value": 5011.96}, {"date": "2024-03-01", "value": 5170.57}, {"date": "2024-04-01", "value": 5112.49}, {"date": "2024-05-01", "value": 5235.23}, {"date": "2024-06-01", "value": 5415.14}, {"date": "2024-07-01", "value": 5538.0}, {"date": "2024-08-01", "value": 5478.21}, {"date": "2024-09-01", "value": 5621.26}, {"date": "2024-10-01", "value": 5792.32}, {"date": "2024-11-01", "value": 5929.92}, {"date": "2024-12-01", "value": 6010.91}, {"date": "2025-01-01", "value": 5979.52}, {"date": "2025-02-01", "value": 6038.69}, {"date": "2025-03-01", "value": 5683.98}, {"date": "2025-04-01", "value": 5369.5}, {"date": "2025-05-01", "value": 5810.92}, {"date": "2025-06-01", "value": 6029.95}, {"date": "2025-07-01", "value": 6296.5}, {"date": "2025-08-01", "value": 6408.95}, {"date": "2025-09-01", "value": 6584.02}, {"date": "2025-10-01", "value": 6735.69}, {"date": "2025-11-01", "value": 6740.89}, {"date": "2025-12-01", "value": 6853.03}, {"date": "2026-01-01", "value": 6929.12}, {"date": "2026-02-01", "value": 6893.81}, {"date": "2026-03-01", "value": 6654.42}, {"date": "2026-04-01", "value": 6957.01}, {"date": "2026-05-01", "value": 7412.55}, {"date": "2026-06-01", "value": 7450.03}], "gas": [{"date": "2000-05-15", "value": 1.676}, {"date": "2000-06-15", "value": 1.669}, {"date": "2000-07-15", "value": 1.754}, {"date": "2000-08-15", "value": 1.72}, {"date": "2000-09-15", "value": 1.869}, {"date": "2000-10-15", "value": 1.856}, {"date": "2000-11-15", "value": 1.811}, {"date": "2000-12-15", "value": 1.726}, {"date": "2001-01-15", "value": 1.646}, {"date": "2001-02-15", "value": 1.682}, {"date": "2001-03-15", "value": 1.738}, {"date": "2001-04-15", "value": 1.837}, {"date": "2001-05-15", "value": 1.993}, {"date": "2001-06-15", "value": 1.975}, {"date": "2001-07-15", "value": 1.817}, {"date": "2001-08-15", "value": 1.608}, {"date": "2001-09-15", "value": 1.708}, {"date": "2001-10-15", "value": 1.592}, {"date": "2001-11-15", "value": 1.403}, {"date": "2001-12-15", "value": 1.204}, {"date": "2002-01-15", "value": 1.231}, {"date": "2002-02-15", "value": 1.319}, {"date": "2002-03-15", "value": 1.507}, {"date": "2002-04-15", "value": 1.657}, {"date": "2002-05-15", "value": 1.617}, {"date": "2002-06-15", "value": 1.633}, {"date": "2002-07-15", "value": 1.648}, {"date": "2002-08-15", "value": 1.637}, {"date": "2002-09-15", "value": 1.627}, {"date": "2002-10-15", "value": 1.579}, {"date": "2002-11-15", "value": 1.624}, {"date": "2002-12-15", "value": 1.585}, {"date": "2003-01-15", "value": 1.662}, {"date": "2003-02-15", "value": 1.853}, {"date": "2003-03-15", "value": 2.15}, {"date": "2003-04-15", "value": 2.092}, {"date": "2003-05-15", "value": 1.89}, {"date": "2003-06-15", "value": 1.809}, {"date": "2003-07-15", "value": 1.789}, {"date": "2003-08-15", "value": 1.913}, {"date": "2003-09-15", "value": 2.068}, {"date": "2003-10-15", "value": 1.839}, {"date": "2003-11-15", "value": 1.74}, {"date": "2003-12-15", "value": 1.681}, {"date": "2004-01-15", "value": 1.722}, {"date": "2004-02-15", "value": 1.914}, {"date": "2004-03-15", "value": 2.143}, {"date": "2004-04-15", "value": 2.185}, {"date": "2004-05-15", "value": 2.298}, {"date": "2004-06-15", "value": 2.322}, {"date": "2004-07-15", "value": 2.233}, {"date": "2004-08-15", "value": 2.131}, {"date": "2004-09-15", "value": 2.115}, {"date": "2004-10-15", "value": 2.376}, {"date": "2004-11-15", "value": 2.35}, {"date": "2004-12-15", "value": 2.143}, {"date": "2005-01-15", "value": 2.016}, {"date": "2005-02-15", "value": 2.163}, {"date": "2005-03-15", "value": 2.346}, {"date": "2005-04-15", "value": 2.596}, {"date": "2005-05-15", "value": 2.52}, {"date": "2005-06-15", "value": 2.41}, {"date": "2005-07-15", "value": 2.559}, {"date": "2005-08-15", "value": 2.721}, {"date": "2005-09-15", "value": 3.032}, {"date": "2005-10-15", "value": 2.926}, {"date": "2005-11-15", "value": 2.57}, {"date": "2005-12-15", "value": 2.319}, {"date": "2006-01-15", "value": 2.424}, {"date": "2006-02-15", "value": 2.54}, {"date": "2006-03-15", "value": 2.624}, {"date": "2006-04-15", "value": 2.925}, {"date": "2006-05-15", "value": 3.337}, {"date": "2006-06-15", "value": 3.26}, {"date": "2006-07-15", "value": 3.26}, {"date": "2006-08-15", "value": 3.212}, {"date": "2006-09-15", "value": 2.937}, {"date": "2006-10-15", "value": 2.593}, {"date": "2006-11-15", "value": 2.508}, {"date": "2006-12-15", "value": 2.587}, {"date": "2007-01-15", "value": 2.616}, {"date": "2007-02-15", "value": 2.713}, {"date": "2007-03-15", "value": 3.105}, {"date": "2007-04-15", "value": 3.339}, {"date": "2007-05-15", "value": 3.485}, {"date": "2007-06-15", "value": 3.329}, {"date": "2007-07-15", "value": 3.174}, {"date": "2007-08-15", "value": 2.948}, {"date": "2007-09-15", "value": 2.922}, {"date": "2007-10-15", "value": 3.112}, {"date": "2007-11-15", "value": 3.394}, {"date": "2007-12-15", "value": 3.353}, {"date": "2008-01-15", "value": 3.296}, {"date": "2008-02-15", "value": 3.231}, {"date": "2008-03-15", "value": 3.609}, {"date": "2008-04-15", "value": 3.846}, {"date": "2008-05-15", "value": 4.015}, {"date": "2008-06-15", "value": 4.531}, {"date": "2008-07-15", "value": 4.511}, {"date": "2008-08-15", "value": 4.128}, {"date": "2008-09-15", "value": 3.842}, {"date": "2008-10-15", "value": 3.44}, {"date": "2008-11-15", "value": 2.507}, {"date": "2008-12-15", "value": 1.871}, {"date": "2009-01-15", "value": 2.051}, {"date": "2009-02-15", "value": 2.265}, {"date": "2009-03-15", "value": 2.239}, {"date": "2009-04-15", "value": 2.377}, {"date": "2009-05-15", "value": 2.531}, {"date": "2009-06-15", "value": 2.969}, {"date": "2009-07-15", "value": 2.92}, {"date": "2009-08-15", "value": 3.057}, {"date": "2009-09-15", "value": 3.169}, {"date": "2009-10-15", "value": 3.062}, {"date": "2009-11-15", "value": 3.006}, {"date": "2009-12-15", "value": 2.964}, {"date": "2010-01-15", "value": 3.065}, {"date": "2010-02-15", "value": 2.993}, {"date": "2010-03-15", "value": 3.104}, {"date": "2010-04-15", "value": 3.138}, {"date": "2010-05-15", "value": 3.136}, {"date": "2010-06-15", "value": 3.134}, {"date": "2010-07-15", "value": 3.171}, {"date": "2010-08-15", "value": 3.186}, {"date": "2010-09-15", "value": 3.064}, {"date": "2010-10-15", "value": 3.146}, {"date": "2010-11-15", "value": 3.205}, {"date": "2010-12-15", "value": 3.297}, {"date": "2011-01-15", "value": 3.389}, {"date": "2011-02-15", "value": 3.576}, {"date": "2011-03-15", "value": 4.002}, {"date": "2011-04-15", "value": 4.206}, {"date": "2011-05-15", "value": 4.229}, {"date": "2011-06-15", "value": 3.965}, {"date": "2011-07-15", "value": 3.844}, {"date": "2011-08-15", "value": 3.823}, {"date": "2011-09-15", "value": 3.971}, {"date": "2011-10-15", "value": 3.89}, {"date": "2011-11-15", "value": 3.848}, {"date": "2011-12-15", "value": 3.648}, {"date": "2012-01-15", "value": 3.747}, {"date": "2012-02-15", "value": 4.027}, {"date": "2012-03-15", "value": 4.414}, {"date": "2012-04-15", "value": 4.292}, {"date": "2012-05-15", "value": 4.353}, {"date": "2012-06-15", "value": 4.133}, {"date": "2012-07-15", "value": 3.821}, {"date": "2012-08-15", "value": 4.109}, {"date": "2012-09-15", "value": 4.211}, {"date": "2012-10-15", "value": 4.458}, {"date": "2012-11-15", "value": 3.893}, {"date": "2012-12-15", "value": 3.628}, {"date": "2013-01-15", "value": 3.678}, {"date": "2013-02-15", "value": 4.127}, {"date": "2013-03-15", "value": 4.192}, {"date": "2013-04-15", "value": 4.031}, {"date": "2013-05-15", "value": 4.051}, {"date": "2013-06-15", "value": 4.05}, {"date": "2013-07-15", "value": 4.056}, {"date": "2013-08-15", "value": 3.919}, {"date": "2013-09-15", "value": 3.989}, {"date": "2013-10-15", "value": 3.829}, {"date": "2013-11-15", "value": 3.641}, {"date": "2013-12-15", "value": 3.642}, {"date": "2014-01-15", "value": 3.666}, {"date": "2014-02-15", "value": 3.726}, {"date": "2014-03-15", "value": 3.984}, {"date": "2014-04-15", "value": 4.21}, {"date": "2014-05-15", "value": 4.22}, {"date": "2014-06-15", "value": 4.163}, {"date": "2014-07-15", "value": 4.11}, {"date": "2014-08-15", "value": 3.961}, {"date": "2014-09-15", "value": 3.821}, {"date": "2014-10-15", "value": 3.585}, {"date": "2014-11-15", "value": 3.234}, {"date": "2014-12-15", "value": 2.916}, {"date": "2015-01-15", "value": 2.596}, {"date": "2015-02-15", "value": 2.756}, {"date": "2015-03-15", "value": 3.388}, {"date": "2015-04-15", "value": 3.261}, {"date": "2015-05-15", "value": 3.804}, {"date": "2015-06-15", "value": 3.596}, {"date": "2015-07-15", "value": 3.812}, {"date": "2015-08-15", "value": 3.594}, {"date": "2015-09-15", "value": 3.175}, {"date": "2015-10-15", "value": 2.945}, {"date": "2015-11-15", "value": 2.819}, {"date": "2015-12-15", "value": 2.776}, {"date": "2016-01-15", "value": 2.823}, {"date": "2016-02-15", "value": 2.477}, {"date": "2016-03-15", "value": 2.679}, {"date": "2016-04-15", "value": 2.822}, {"date": "2016-05-15", "value": 2.855}, {"date": "2016-06-15", "value": 2.93}, {"date": "2016-07-15", "value": 2.911}, {"date": "2016-08-15", "value": 2.745}, {"date": "2016-09-15", "value": 2.803}, {"date": "2016-10-15", "value": 2.862}, {"date": "2016-11-15", "value": 2.788}, {"date": "2016-12-15", "value": 2.738}, {"date": "2017-01-15", "value": 2.848}, {"date": "2017-02-15", "value": 2.946}, {"date": "2017-03-15", "value": 3.059}, {"date": "2017-04-15", "value": 3.067}, {"date": "2017-05-15", "value": 3.101}, {"date": "2017-06-15", "value": 3.08}, {"date": "2017-07-15", "value": 3.005}, {"date": "2017-08-15", "value": 3.073}, {"date": "2017-09-15", "value": 3.22}, {"date": "2017-10-15", "value": 3.137}, {"date": "2017-11-15", "value": 3.294}, {"date": "2017-12-15", "value": 3.187}, {"date": "2018-01-15", "value": 3.269}, {"date": "2018-02-15", "value": 3.418}, {"date": "2018-03-15", "value": 3.476}, {"date": "2018-04-15", "value": 3.617}, {"date": "2018-05-15", "value": 3.69}, {"date": "2018-06-15", "value": 3.673}, {"date": "2018-07-15", "value": 3.605}, {"date": "2018-08-15", "value": 3.556}, {"date": "2018-09-15", "value": 3.588}, {"date": "2018-10-15", "value": 3.76}, {"date": "2018-11-15", "value": 3.632}, {"date": "2018-12-15", "value": 3.368}, {"date": "2019-01-15", "value": 3.232}, {"date": "2019-02-15", "value": 3.236}, {"date": "2019-03-15", "value": 3.342}, {"date": "2019-04-15", "value": 3.894}, {"date": "2019-05-15", "value": 4.019}, {"date": "2019-06-15", "value": 3.787}, {"date": "2019-07-15", "value": 3.668}, {"date": "2019-08-15", "value": 3.555}, {"date": "2019-09-15", "value": 3.687}, {"date": "2019-10-15", "value": 4.116}, {"date": "2019-11-15", "value": 3.944}, {"date": "2019-12-15", "value": 3.61}, {"date": "2020-01-15", "value": 3.489}, {"date": "2020-02-15", "value": 3.447}, {"date": "2020-03-15", "value": 3.262}, {"date": "2020-04-15", "value": 2.827}, {"date": "2020-05-15", "value": 2.771}, {"date": "2020-06-15", "value": 2.972}, {"date": "2020-07-15", "value": 3.102}, {"date": "2020-08-15", "value": 3.156}, {"date": "2020-09-15", "value": 3.174}, {"date": "2020-10-15", "value": 3.137}, {"date": "2020-11-15", "value": 3.115}, {"date": "2020-12-15", "value": 3.143}, {"date": "2021-01-15", "value": 3.262}, {"date": "2021-02-15", "value": 3.434}, {"date": "2021-03-15", "value": 3.781}, {"date": "2021-04-15", "value": 3.911}, {"date": "2021-05-15", "value": 4.068}, {"date": "2021-06-15", "value": 4.182}, {"date": "2021-07-15", "value": 4.253}, {"date": "2021-08-15", "value": 4.319}, {"date": "2021-09-15", "value": 4.31}, {"date": "2021-10-15", "value": 4.4}, {"date": "2021-11-15", "value": 4.598}, {"date": "2021-12-15", "value": 4.597}, {"date": "2022-01-15", "value": 4.584}, {"date": "2022-02-15", "value": 4.66}, {"date": "2022-03-15", "value": 5.655}, {"date": "2022-04-15", "value": 5.692}, {"date": "2022-05-15", "value": 5.871}, {"date": "2022-06-15", "value": 6.294}, {"date": "2022-07-15", "value": 5.897}, {"date": "2022-08-15", "value": 5.333}, {"date": "2022-09-15", "value": 5.375}, {"date": "2022-10-15", "value": 5.905}, {"date": "2022-11-15", "value": 5.173}, {"date": "2022-12-15", "value": 4.418}, {"date": "2023-01-15", "value": 4.368}, {"date": "2023-02-15", "value": 4.591}, {"date": "2023-03-15", "value": 4.786}, {"date": "2023-04-15", "value": 4.787}, {"date": "2023-05-15", "value": 4.74}, {"date": "2023-06-15", "value": 4.781}, {"date": "2023-07-15", "value": 4.823}, {"date": "2023-08-15", "value": 5.13}, {"date": "2023-09-15", "value": 5.52}, {"date": "2023-10-15", "value": 5.546}, {"date": "2023-11-15", "value": 4.935}, {"date": "2023-12-15", "value": 4.558}, {"date": "2024-01-15", "value": 4.482}, {"date": "2024-02-15", "value": 4.535}, {"date": "2024-03-15", "value": 4.831}, {"date": "2024-04-15", "value": 5.255}, {"date": "2024-05-15", "value": 5.118}, {"date": "2024-06-15", "value": 4.777}, {"date": "2024-07-15", "value": 4.59}, {"date": "2024-08-15", "value": 4.451}, {"date": "2024-09-15", "value": 4.574}, {"date": "2024-10-15", "value": 4.513}, {"date": "2024-11-15", "value": 4.355}, {"date": "2024-12-15", "value": 4.243}, {"date": "2025-01-15", "value": 4.31}, {"date": "2025-02-15", "value": 4.59}, {"date": "2025-03-15", "value": 4.608}, {"date": "2025-04-15", "value": 4.764}, {"date": "2025-05-15", "value": 4.743}, {"date": "2025-06-15", "value": 4.571}, {"date": "2025-07-15", "value": 4.397}, {"date": "2025-08-15", "value": 4.41}, {"date": "2025-09-15", "value": 4.557}, {"date": "2025-10-15", "value": 4.54}, {"date": "2025-11-15", "value": 4.571}, {"date": "2025-12-15", "value": 4.299}, {"date": "2026-01-15", "value": 4.128}, {"date": "2026-02-15", "value": 4.454}, {"date": "2026-03-15", "value": 5.379}, {"date": "2026-04-15", "value": 5.844}, {"date": "2026-05-15", "value": 6.067}]};

function initEventImpactMap() {
  const root = document.getElementById('event-impact-app');
  if (!root || root.dataset.eventImpactInited) return;
  root.dataset.eventImpactInited = 'true';

  // ---------- prep series ----------
  function prep(series){
    return series.map(d => ({date: new Date(d.date), value: d.value})).sort((a,b)=>a.date-b.date);
  }
  const spSeries = prep(DATA.sp500);
  const gasSeries = prep(DATA.gas);
  const events = DATA.events.map(e => ({name: e.name, date: new Date(e.date)})).sort((a,b)=>a.date-b.date);

  function findBaselineIdx(series, date){
    // last index with series date <= given date
    let lo = 0, hi = series.length - 1, ans = -1;
    while(lo <= hi){
      const mid = (lo+hi) >> 1;
      if(series[mid].date <= date){ ans = mid; lo = mid+1; } else { hi = mid-1; }
    }
    return ans;
  }

  function computeMovements(series, windowN){
    const out = [];
    for(const ev of events){
      const bIdx = findBaselineIdx(series, ev.date);
      const tIdx = bIdx + windowN;
      if(bIdx < 0 || tIdx >= series.length) continue; // insufficient data for this window
      const base = series[bIdx], target = series[tIdx];
      const net = target.value - base.value;
      const pct = base.value !== 0 ? (net / base.value) * 100 : 0;
      out.push({
        name: ev.name,
        date: ev.date,
        baseDate: base.date,
        targetDate: target.date,
        baseValue: base.value,
        targetValue: target.value,
        net: net,
        pct: pct
      });
    }
    return out;
  }

  // ---------- state ----------
  let metric = 'sp500';
  let windowN = 3;

  const fmtMonth = d3.timeFormat('%b %Y');
  const fmtDate = d3.timeFormat('%b %d, %Y');
  const fmtPts = d3.format('+,.1f');
  const fmtDollars = d3.format('+,.3f');
  const fmtPct = d3.format('+.1f');

  const metricLabels = {
    sp500: { unit: 'pts', name: 'S&P 500', fmt: fmtPts, dollar: false },
    gas:   { unit: '$/gal', name: 'CA Gas Price', fmt: fmtDollars, dollar: true }
  };

  // ---------- render ----------
  const svg = d3.select(root).select('#chart');
  const wrap = root.querySelector('#chart-wrap');
  const tooltip = d3.select(root).select('#tooltip');

  function render(){
    const series = metric === 'sp500' ? spSeries : gasSeries;
    const info = metricLabels[metric];
    const rows = computeMovements(series, windowN);

    root.querySelector('#window-val').textContent = windowN + (windowN===1 ? ' month' : ' months');
    root.querySelector('#metric-label').innerHTML =
      `${info.name} &mdash; % change, event month &rarr; +${windowN} mo`;

    const emptyNote = root.querySelector('#empty-note');
    if(rows.length === 0){
      svg.selectAll('*').remove();
      emptyNote.style.display = 'block';
      return;
    }
    emptyNote.style.display = 'none';

    const width = Math.max(320, wrap.clientWidth - 28);
    const height = 560;
    svg.attr('viewBox', [0,0,width,height]).attr('width', width).attr('height', height);

    const maxAbsPct = d3.max(rows, d => Math.abs(d.pct)) || 1;
    const color = d => d.net >= 0 ? 'var(--up)' : 'var(--down)';
    const opacityScale = d3.scaleSqrt().domain([0, maxAbsPct]).range([0.35, 1]);

    const treeRoot = d3.hierarchy({children: rows})
      .sum(d => Math.max(Math.abs(d.pct), maxAbsPct*0.002))
      .sort((a,b) => b.value - a.value);

    d3.treemap()
      .size([width, height])
      .paddingInner(2)
      .paddingOuter(2)
      .round(true)
      (treeRoot);

    svg.selectAll('*').remove();

    const cell = svg.selectAll('g.cell')
      .data(treeRoot.leaves())
      .join('g')
      .attr('class','cell')
      .attr('transform', d => `translate(${d.x0},${d.y0})`);

    cell.append('rect')
      .attr('width', d => d.x1 - d.x0)
      .attr('height', d => d.y1 - d.y0)
      .attr('fill', d => color(d.data))
      .attr('fill-opacity', d => opacityScale(Math.abs(d.data.pct)))
      .attr('rx', 3);

    cell.each(function(d){
      const w = d.x1 - d.x0, h = d.y1 - d.y0;
      const g = d3.select(this);
      const pad = 8;
      if(w < 34 || h < 24) return; // too small for any text

      const nameSize = w > 140 ? 12.5 : 10.5;
      const canShowVal = h > 40;
      const canShowDate = h > 62 && w > 90;

      // wrap name into up to 2 lines
      const words = d.data.name.split(' ');
      let lines = [''];
      const maxCharsPerLine = Math.max(8, Math.floor(w / (nameSize*0.56)));
      words.forEach(word => {
        const cur = lines[lines.length-1];
        const trial = cur ? cur + ' ' + word : word;
        if(trial.length > maxCharsPerLine && cur){
          if(lines.length < 3) lines.push(word);
          else lines[lines.length-1] = cur; // drop overflow words
        } else {
          lines[lines.length-1] = trial;
        }
      });
      lines = lines.slice(0, h > 70 ? 3 : 2);

      lines.forEach((line,i) => {
        g.append('text')
          .attr('class','name')
          .attr('x', pad).attr('y', pad + (i+1)*nameSize*1.05)
          .attr('font-size', nameSize)
          .text(line + (i === lines.length-1 && lines.length < d.data.name.split(' ').length && d.data.name.split(' ').length > lines.reduce((a,l)=>a+l.split(' ').length,0) ? '…' : ''));
      });

      if(canShowVal){
        const valStr = info.fmt(d.data.net) + ' ' + info.unit;
        g.append('text')
          .attr('class','val')
          .attr('x', pad)
          .attr('y', h - (canShowDate ? 22 : 8))
          .attr('font-size', w > 140 ? 13 : 11)
          .text(valStr + '  (' + fmtPct(d.data.pct) + '%)');
      }
      if(canShowDate){
        g.append('text')
          .attr('class','date')
          .attr('x', pad)
          .attr('y', h - 8)
          .attr('font-size', 9.5)
          .text(fmtMonth(d.data.date));
      }
    });

    cell
      .on('mousemove', function(event, d){
        const info2 = metricLabels[metric];
        const dirWord = d.data.net >= 0 ? 'gained' : 'lost';
        tooltip.style('opacity', 1)
          .style('left', (event.clientX + 16) + 'px')
          .style('top', (event.clientY + 16) + 'px')
          .html(`
            <div class="t-name">${d.data.name}</div>
            <div class="t-row"><span>Event date</span><b>${fmtDate(d.data.date)}</b></div>
            <div class="t-row"><span>${info2.name} ${dirWord}</span><b>${info2.fmt(d.data.net)} ${info2.unit}</b></div>
            <div class="t-row"><span>% change</span><b>${fmtPct(d.data.pct)}%</b></div>
            <div class="t-row"><span>Baseline (${fmtMonth(d.data.baseDate)})</span><b>${d3.format(',.2f')(d.data.baseValue)}</b></div>
            <div class="t-row"><span>+${windowN}mo (${fmtMonth(d.data.targetDate)})</span><b>${d3.format(',.2f')(d.data.targetValue)}</b></div>
          `);
      })
      .on('mouseleave', () => tooltip.style('opacity', 0));
  }

  // ---------- controls wiring ----------
  root.querySelector('#metric-seg').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if(!btn) return;
    metric = btn.dataset.metric;
    root.querySelectorAll('#metric-seg button').forEach(b => b.classList.toggle('active', b === btn));
    render();
  });

  root.querySelector('#window-slider').addEventListener('input', (e) => {
    windowN = +e.target.value;
    render();
  });

  window.addEventListener('resize', render);
  render();
}

window.initEventImpactMap = initEventImpactMap;
