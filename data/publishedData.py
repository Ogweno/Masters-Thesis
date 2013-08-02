import json

data = """AP3N 69.459 -84.462 POLARIS 60 40.1 0.8 1.711 0.017 40.6 0.5 1.714 0.013
ARVN 61.098 -94.070 POLARIS 41 41.0 1.5 1.751 0.037 41.4 0.7 1.740 0.022
B1NU 68.462 -71.588 CHASME 40 43.5 2.0 1.706 0.032 43.9 2.2 1.695 0.040
B2NU 68.922 -73.197 CHASME 14 42.3 7.3 1.709 0.039 43.3 5.8 1.714 0.070
BULN 66.397 -93.125 POLARIS 85 37.5 0.3 1.696 0.010 38.1 0.4 1.692 0.011
CRLN 64.189 -83.348 NERC 31 35.4 0.6 1.740 0.018 36.0 0.4 1.732 0.018
CTSN 62.852 -82.485 NERC 58 36.1 0.4 1.757 0.017 36.6 0.5 1.757 0.024
DORN 64.230 -76.531 NERC 51 36.2 0.3 1.768 0.010 36.5 0.4 1.770 0.011
FCC 58.762 -94.087 CNSN 160 40.4 0.8 1.764 0.016 40.6 1.8 1.761 0.034
FRB 63.747 -68.547 CNSN 247 43.3 0.2 1.760 0.006 43.5 0.2 1.748 0.006
GIFN 69.994 -81.638 POLARIS 138 41.2 0.1 1.726 0.005 41.5 0.2 1.723 0.007
ILON 69.371 -81.824 POLARIS 142 37.7 0.2 1.722 0.006 38.4 0.3 1.713 0.007
INUQ 58.451 -78.119 POLARIS 77 41.6 0.4 1.735 0.014 41.8 0.5 1.731 0.016
IVKQ 62.418 -77.911 POLARIS 90 35.9 0.2 1.756 0.009 36.3 0.2 1.746 0.014
JOSN 63.162 -91.542 POLARIS 36 37.0 2.5 1.743 0.028 37.5 0.7 1.740 0.025
KIMN 62.851 -69.879 NERC 44 44.1 3.0 1.755 0.044 44.8 2.6 1.746 0.028
KUGN 68.090 -90.062 POLARIS 21 34.5 2.5 1.743 0.063 35.1 3.3 1.739 0.062
LAIN 69.109 -83.536 POLARIS 55 39.3 0.3 1.764 0.012 39.8 0.4 1.744 0.016
MANN 62.289 -79.592 NERC 27 34.9 0.4 1.769 0.016 35.4 0.6 1.746 0.020
MNGN 64.663 -72.434 NERC 61 42.8 0.5 1.735 0.011 43.4 1.1 1.724 0.015
NOTN 63.294 -78.135 NERC 32 36.0 0.3 1.747 0.013 36.3 0.4 1.746 0.016
NUNN 65.215 -91.078 POLARIS 50 36.4 0.4 1.726 0.015 37.2 0.4 1.706 0.015
PINU 72.697 -77.975 CHASME 20 33.8 7.2 1.739 0.103 34.6 4.7 1.706 0.066
PNGN 66.143 -65.712 NERC 17 35.1 0.9 1.696 0.032 37.6 6.2 1.667 0.117
QILN 66.653 -86.371 POLARIS 145 37.0 0.2 1.723 0.010 37.5 0.3 1.718 0.013
SBNU 69.540 -93.557 CHASME 20 36.1 0.7 1.724 0.036 35.6 2.7 1.747 0.051
SEDN 63.250 -91.208 POLARIS 71 36.2 6.4 1.774 0.143 39.4 6.2 1.715 0.125
SHMN 64.577 -84.115 NERC 34 37.0 0.3 1.720 0.011 37.2 0.4 1.725 0.019
SHWN 63.775 -85.089 NERC 53 37.5 0.4 1.711 0.013 38.0 0.5 1.702 0.017
SNQN 56.542 -79.225 POLARIS 67 36.1 8.0 1.975 0.113 29.1 20.2 1.901 0.152
SRLN 68.551 -83.324 POLARIS 105 37.7 0.3 1.721 0.008 38.2 0.4 1.708 0.012
STLN 67.312 -92.985 POLARIS 73 38.6 0.3 1.709 0.008 39.1 0.4 1.686 0.012
WAGN 65.879 -89.445 POLARIS 47 34.0 0.4 1.721 0.016 34.5 0.8 1.695 0.019
YBKN 64.319 -96.003 POLARIS 45 34.9 0.4 1.757 0.017 35.1 0.4 1.766 0.025
YRTN 62.810 -92.110 POLARIS 105 31.3 8.9 1.906 0.243 36.9 5.4 1.759 0.134"""



stnd = {}
for line in data.split("\n"):
    fields = line.split()
    stn = fields[0]
    stnd[stn] = {}
    stnd[stn]["H"] = float(fields[5])
    stnd[stn]["stdH"] = float(fields[6])
    stnd[stn]["R"] = float(fields[7])
    stnd[stn]["stdR"] = float(fields[8])



open("thompsonPaper.json",'w').write( json.dumps(stnd, sort_keys = True, indent = 2 ))

