
# 0_ europe
# 1_ asia
# 2_ australia
# 3_ africa
# 4_ south america
# 5_ north america

dest = {'0_01_Israel': [1981134,1371721,384062,2246907,1337403,384056,384077,384085,
                        384042,382802,1332273,1240469,1347906,1330054,1819903],
        '0_02_Turkey': [158125,158234],
        '0_03_Black Sea':[89652,416351,2104634,2086905,158017,2474595,2656615,
                          1211774,2739435],
        '0_04_Greece':[721969,1245609,935222,1719137,1668534,569717,569410,1665873,
                       911089,911103,911096,911095,660931,2515446],
        '0_05_Baltikum':[2090864],
        '0_06_Italy_East':[2146941,2098105,10102,1841352,2219645,2219648,2220293,
                           2220829,2220832,2220836,2220837,2220298,2230422,
                           2250853,2498155,2498159,2498211,2498205,2498210,
                           2498203,2498209,2498206,2498204,2498207,2498208,
                           2498212,2498213,2506846,2506839,2506850,2506840,
                           2506853,2506852,2506854,2506848,2506845,2531017,
                           2531018,2531011,2531014,2531012,2220840],
        '0_06_Italy_South':[2531549,2531550,2531552,2531547,2531554,2531553,
                            2569951,2569952,2569954,2569955,2569956,2569956,
                            2569957,2569976,2569977,2569978,2569979,2569980,
                            2569981,2569982,2569983,2569984],
        '0_07_Italy_West':[1827384,2146938,1907517,1116884,2570012,2570703,   #including sicilia
                           2573898,2573901,2573902,2573903,2573904,2573905,
                           2573907,2573910,2535730,2575553,2575554,2575556,
                           2575557,2575558,2870975],  
        '0_08_France_South':[1075117,1075289,1075699,1076176,1082657,1104548,1105489,1111444,
                             1162753,1229390,1229554,1232038,1232040,1601662,449325,
                             1162751,1804442,1108344,1108335,1281435,1281435,
                             1344613,1162743,1601653,1951715,1646871],  #including corse
        '0_09_Spain_East_South':[331157,2118550,290000,1927491,2118665,2127497,331718,
                                 289968,2813653,2939479],
        '0_10_Portugal':[312994,2127463,1226237,2448396,2383409,2566010,2579329,
                         3579325,2579336,2579330,2579322,2579368,2579365,2579366,
                         2579325,2566210,2848635],
        '0_11_Spain_North':[2631375,2655323,2763702,2639626,2827450,2916156],
        '0_12_France_West':[1082413,1727809,1838226,132818,1113425,1591337,70423,
                            68152,116984,961832,299601,1782920,1613165,1102138,2165837,
                            2569995],
        '0_13_France_North':[962076,1242254,1291867,1075690,1075956,1202873,1202891,
                             1259838,1260107,1260209,136211,1590126,379638,1084080,961897,
                             1239915,1249077,1249085,1261528,1249090,1075407,1202842,
                             1976129,961898,951272,1262716,1249816,1536798,1204782,
                             2251000,1778261,1778255,2587230,2527809,1200089],
        '0_14_North_Sea':[1239327,1075197,123924,370068,123751,123822,1376256,1754272,385574,
                          385584,386243,400268,400269,531186,535594,535603,953587,2123539,
                          2237871,1061113,385578,1364262,324288,2675284,2651958,
                          2737246,2737124],
        '0_15_East_Sea':[387605,409057,410298,412391,535612,535631,535949,1459770,
                         1459771,1459772,409071,1645604,34392,2835045,
                         2835046,2917559,2917558,2917331], #including poland
        '0_16_Baltikum':[2237066,189775,549362,2811903,2067229],
        '0_17_Finnland_South':[2822446,2835014],
        '0_18_Sweden':[2296518],
        '0_19_Norway':[1729367,1113591,1729213,1729230,1730537],
        '0_20_Russia_North_west_of_Ural':[191580,2173454,255345,255408,281783,2469254,
                                          2521343,2520348,2561580,2702707,192300,
                                          2811301,2730723],
        '0_21_Caspian Sea':[1730417,214415,2103591,2471690,2910949],
        '0_22_Island':[906365],
        '0_23_Great_Britain':[2267039,2263653,2650612,2678556,14304,454800,
                              2713641,1455110,2659911,2661315,2668445,2794974,
                              2794964,2794973,2795108,2795123,2795129,2795138,
                              2795089,2798097, 2863249,2863261,2863274,
                              2863407,2863468,2863289,2871746,2873828,
                              2873839,2877467,2877486,2877495,2878049,
                              2878256,2878257,2878273,2887914,2887915,
                              2889926,2889927,2889932,2889958,2889959,
                              2890569,2890568,2890566,2890565,2890564,
                              2887920,2890562,2922145,2922148,3259554,
                              3261984,3224166],
        '0_24_Ireland':[2712762],
        '0_25_Europe_endhoric':[2216891],
        

        '1_01_Russia_North_east_of_Ural':[192347,170956,2178464,2178463,2178462,178535,
                                          179500,178078,2176171,2246098,2175573,176123,
                                          2164950,191377,1076099,206484,2172338,173215,
                                          170226,170956,185104,2166081,181988,206490,
                                         166171],
        '1_02_Russia_East':[197653,198454,2100289,2444583,2418190,2254611,2254152,
                            2191957,2523275,2517500,2513346,2512417,2454712,2469401,
                            2469922,2506672,2580758,2567774,2564387,2563573,2551170,
                            2549987,2541264,2531253,2729052,2701977,2699557,2691089,
                            2682934,2619372,2622959,2797631,2795155],
        '1_02_Japan': [2431268,2354599,2354389,2354380,2352921,2352952,2771133],
        '1_03_China':[215336,405843,553298,2246137,2246264,171843,904508,396420,
                      2811414],
        '1_04_Vietnam':[215354,393967,215411,231955,2155608,454994],
        '1_04_Thailand':[228063,237205,233960,2676664],
        
        '1_09_India_East':[330736,1236345,1243337,337204,2826093],
        '1_10_India_West':[1159233,2710477,2708786],
        '1_20_Arabia':[1246863,2632550],  # including

        '1_30_Asia_endoric':[223008,1103172,2721433,2162521,2470221],

        '2_01_Australia_WA':[2207435,2211617,2214237,2723390],
        '2_02_Australia_NT':[2580437],
        '2_03_Australia_QL':[1651587,2139595,1705333,2205411,2211732,2214235,2723296,
                             2723305,2723293,2723358],
        '2_04_Australia_NSW':[962794,1542972,2137075,2139761,2205292,2205293,2205672,
                              2214229,2237757,2214248,2593941,2205422,2563941,
                              2723370,2775616],
        '2_05_Australia_VT':[2137075,2195640,2205422,2205425,2205694,2211681,2237751,2229052,
                             2305275,2421867,2723291,2723369],
        '2_06_Australia_SA':[108680,16853,17120,73256,7562,88947,38249,38277,116629,122244,
                             124281,1435821,17824,19958,2137129,61090,6188,6637,6883,2203587,
                             2403773,2401611,2723343],
        '2_07_Australia_endhoric':[2205453,2246968],
        '2_08_Tasmania':[2128928,2214146,2214192,279903,2584571],
        '2_20_Newzealand':[2172478],
        '2_50_Oceania':[312651,313052,313138,313155,1127103,313474,2190743,2190741,
                        305535,2188754,302110,317445,611307,316367,402216,325757,
                        659650,298611,2473106,317405,2190742,2913758],

        '3_01_Africa_North':[50793,2779692,2778232],
        '3_02_Africa_East':[960819,960818,960706,960080,318455,1528015,1576044,2469786,
                            2635247,2634097,2633895,2627078,2679385,1185388,2780150,
                            2780170,2778226,2778230,2778235,2778920,2780298],
        '3_03_Africa_West':[2237396,2175718,1394726,2248461,2168051,2280350,2280351,
                            2631331,2634846,2679615,1187215,1189421,1191530,1191568,
                            1192473,1199972,1200379,1201377,1202937,1205202,1205528,
                            1206559,2708775,2729269,2728656,2728653,2728560,2728556,
                            2728555,2725194,2721666,2718394,2760250,2741967,2741966,
                            2741963,2741797,2740819,2734863,2779652,2778904,2864624,
                            2813084],
        '3_04_Africa_endoric':[2631912,2765607,2715490,2777900,2775504],
        '3_05_Africa_Madagascar':[2262762,1154493,1154508,1154531,1154545,1154755,1154699,
                                  1154994,1154902,1154755,1155647,1155681,1155709,1155731,
                                  1155943,1165396,1165480,1165509,1154522,2278446,2262931,
                                  1154623,1155730,1165500,1155963],
        '3_06_Africa_Canaria':[2578090,2570478,2634294,69145],

        '4_01_Chile':[2237689,2634345,2736705,2736796,2737118],
        '4_02_Peru':[2113980],
        '4_03_Ecuador':[2113951,2127886,2113957,2737803,2828760],
        '4_04_Colombia':[2140749,1301124],
        '4_05_Venezuela':[1084627],
        '4_06_Guyana':[2394951,2736317],
        '4_07_Brasil_North':[2295651,1083284,1110121,1267457,2736114],
        '4_08_Brasil_South':[2736329,2737852,1360217,2844355],
        '4_09_Uruguay':[2738222,2736318],
        '4_10_Argentina':[421678,380835,1953254,2640720,2736026,2736631,2737030,
                          2737164,3128523],
        '4_11_South-America_endoric':[1181004],

        '5_00_USA_Florida':[2193475,2193569,2193565,2193563,2193562,2193561,2193561,
                            2193554,2193549,2193544,2193543,2193542,2193539,2193526,
                            2193527,2193524,2193520,2193520,2193513,2193510,2193501,
                            2193490,2193487,2193486,2193484,2193481,2193477,2193469,
                            2193466,2193461,2193558,1272572,1101516,1613911,2193516],
        '5_00_USA_South':[2193573,2193568,2193559,2193534,2193525,2193489,2193485,
                          2193479,2193476,2193470,2193468,2192747,2192739,1756854,
                          2191457,2183784,2183780,2182455,2185957,2472419],
        '5_01_USA_East':[2148192,1984261,227238,1339083,371307,2188458,1346220,
                         1347686,2183775,1658933,2193560,2636997,2699338,
                         374451,2749972,2739614,2737897,2213787],
        '5_02_USA_4Lakes':[2148129,2245991,2192735,2192733,2191462,299120],
        '5_02_USA_endoric':[2811034,2461759],
        '5_03_Canada_East':[2147298],
        '5_04_Canada_North':[],
        '5_05_Alaska':[],
        '5_06_Canada_West':[],
        '5_07_USA_West':[2718127],
        '5_08_middle_america_east':[2557514,2716682],
        '5_09_middle_america_west':[],
        
        '5_99_Haiti':[1247553,1240526,1242983,1244309,1243038,1242550,1262961,
                      1245051,1243850,1243828,1243784,1243783,1243781,1243780,
                      1242966,1242965,390103,1241473,1257847,1257841,1241452,
                      1240658,1240631,1247311,1251743,1253749,1253790,1271847,
                      1254818,1253843,1253841,417630,1243782,398310,2432993,
                      2684539,2646089]
        }
