#!/usr/bin/python2
#
# python-mode indent C-c < or C-c >
# python-mode comment/uncomment region M-;

###########################################################################
# IMPORTS
###########################################################################
import os, json
import fnmatch
import numpy as np
from dbutils import queryStns, Scoper
#import matplotlib.pyplot as plt
#import numpy as np
#from scipy.signal import detrend
#from scipy.stats import pearsonr
#from matplotlib.backends.backend_pdf import PdfPages

from itertools import chain



def find(seq, pattern):
    pattern = pattern.lower()
    for i, n in enumerate(seq):
        if fnmatch.fnmatch(n.lower(), pattern):
             return i
    return -1

def index(seq, pattern):
    result = find(seq, pattern)
    if result == -1:
        raise ValueError
    return result

def isin(seq, pattern):
    result = find(seq, pattern)
    if result == -1:
        return False
    else:
        return True


class Args(object):
    def __init__(self):
        self.stationList = False
        self.attribute = False
        self.query = False
        self.Keys = False

    def addQuery(self, attr, op, value):
        self.query = [attr, op, value]

    def addKeys(self):
        self.keys = True

class Params(object):
    def __init__(self, fname, args, plist):
        """ Takes a file name to json formatted data
        with a bunch of stations as primary attributes, each with
        a value that is also an attribute. whatever"""
        self._stns = [] # Base data
        self.stns = [] # Filtered data
        self.plist = plist
        # scoper provides some utilites for working with scoped declarations for
        # accessing deep json structures
        self.scp = Scoper("::")

        rawdata = json.loads( open(fname).read() )
        filtdata = queryStns(rawdata, args, self.scp)



        for stn in filtdata.keys():
            # Make sure all parameters exist for each station
            # If they do, add station to list.
            # Use the scoper to flatten json so we can check if
            # scoped keys are in the dictionary. (allows us to search with
            # depth into dictionary a::b = d['a']['b']
            if len([p for p in plist if p in self.scp.flattendict(filtdata[stn])]) == len(plist):
                self._stns.append(stn)

        # Make self._stns immutable
        self._stns = tuple(self._stns)
        # Create a temporary dictionary of all
        # station data.
        temp = {}
        for p in plist:
            temp[p] = np.zeros(len(self._stns))
        for ii, stn in enumerate(self._stns):
            for p in plist:
                temp[p][ii] = self.scp.flattendict(filtdata[stn])[p]

        # Build base data variables with _ prefix as
        # numpy data extracted from json data.
        for p in plist:
            setattr(self, '_' + self.scp.normscope(p), temp[p])

        # Build variable list
        self.orderAttribs([i for i in range(len(self._stns))])

    def sync(self, pobj):
        """ Filter by list of stations only, useful for syncing
        with another Param object station list. The incoming
        station list must be subset of object station list or an
        error is raised."""
#        stns = []
        myInds = []
        yourInds = []
        # Scan down callee's station list
        for ind, stn in enumerate(pobj.stns):
            # Look for the stn in the callee and find the index in self
            ix = find(self._stns, stn)
            # If we don't have a stn, we skip an ind in the callee's index list
            if ix == -1:
                pass
            else:
                myInds.append(ix)
                yourInds.append(ind)

        pobj.orderAttribs(yourInds)
        self.orderAttribs(myInds)

    def orderAttribs(self, index):
        """ Take a list of index of length len(self.stns)
        holding indice numbers to reorganize attribute vectors"""
        # For each base attribute make a new attribute with name minus underscore
        # which has the value of the inds sorted array.
        self.stns = np.take(self._stns, index)
        for p in self.plist:
            setattr(self, self.scp.normscope(p),
                    np.take(getattr(self, '_'+ self.scp.normscope(p)),
                            index))



if __name__  == "__main__":
    pass

## Setup pdf printer
#    pp = PdfPages('correlations.pdf')
### Load data

#    mb = Params( os.environ['HOME'] + '/thesis/stations.json', ["Vp","H","R"])

#(os.environ['HOME'] + '/thesis/stnchrons.json')
#    kn = Params(os.environ['HOME'] + '/thesis/kanStats.json', ["H","R"])
#    d3 = Params(os.environ['HOME'] + '/thesis/3DStats.json', ["Vp","H","R"])






# for i in range(5, 4, -1):

#     stdVp[i] = 0.1*i
#     args = Args()
#     args.stationList ="ACKN AP3N CLPO COWN DELO DSMN DVKN FRB GALN GIFN ILON LAIN MALO MLON ORIO PEMO PLVO SEDN SILO SNPN SRLN TYNO ULM WAGN WLVO YBKN YOSQ"
#     args.addQuery("status","in", "processed")


#     plottype = ["param","geochron", "kanamori"][0]


    #### Kanamori data
#     if "kanamori" in plottype:

#         ### Regression Line 3D Gsearch
#         A = np.vstack([H, np.ones(len(H))]).T
#         m, c = np.linalg.lstsq(A, R)[0]
#         regrB = m*H + c

#         ### Regression Line Kanamori
#         A = np.vstack([Hk, np.ones(len(Hk))]).T
#         mk, ck = np.linalg.lstsq(A, Rk)[0]
#         regrK = mk * Hk + ck

#         ### RMS before 3D Gsearch detrending
#         Rdiff = Rk - R
#         RMS = np.sqrt(1.0 / len(Rdiff) * np.dot(Rdiff.T, Rdiff))

#         # Detrend Vp/Vs 3D Gsearch data
#         Rdtr = R - (regrB -  np.mean(regrB))

#         plt.figure(num = 1 - i, figsize = (10,12) )
#         # see http://matplotlib.org/examples/pylab_examples/subplots_demo.html
#         ax1 = plt.subplot(211)
#         plt.plot(Hk, Rk, 'ob', label = 'Vp/Vs Kanamori')
#         plt.plot(Hk, regrK, 'b', label = "Kanamori fit")
#         plt.plot(H, R, 'or', label = '3D Gsearch Vp/Vs')
#         plt.plot(H, regrB, 'r', label = "3D Gsearch fit" )
#         plt.title("For Stations with Vp err < {}\nVp/Vs for 3D Gsearch and Kanamori as a function of crustal thickness H".format(stdVp))
#         plt.ylabel("Vp/Vs")
#         plt.ylim((1.6, 2.0))
#         plt.xlim((25, 50))
#         plt.setp( ax1.get_xticklabels(), visible=False)
#         plt.legend(loc=2)

#         ### New regression line for 3D Gsearch data (should have slope = 0)
#         A = np.vstack([H, np.ones(len(H))]).T
#         m, c = np.linalg.lstsq(A, Rdtr)[0]
#         regrDtr = m*H + c

#         ### RMS after 3D Gsearch detrending
#         Rdiff = Rk - Rdtr
#         RMSdtr = np.sqrt(1.0 / len(Rdiff) * np.dot(Rdiff.T, Rdiff))

#         # see http://matplotlib.org/examples/pylab_examples/subplots_demo.html
#         plt.subplot(212)
#         plt.plot(Hk, Rk, 'ob', label = 'Vp/Vs Kanamori')
#         plt.plot(Hk, regrK, 'b', label = "Kanamori fit" )
#         plt.plot(H, Rdtr, 'or', label = '3D Gsearch Vp/Vs')
#         plt.plot(H, regrDtr, 'r', label = "3D Gsearch fit" )
#         plt.title("Vp/Vs with Linear Trend removed in 3D Gsearch data as a function of crustal thickness H")
#         plt.ylabel("Vp/Vs")
#         plt.ylim((1.6, 2.0))
#         plt.xlim((25, 50))
#         plt.xlabel('Crustal Thickness [km]')
#         plt.legend(loc=2)

#         pp.savefig()


#         ns = np.arange(len(Hk))

#         plt.figure(num = 16 - i, figsize = (10, 12))
#         ax1 = plt.subplot(211)
#         plt.plot(ns, Rk, 'ob', label = 'R Kanamori')
#         plt.plot(ns, R, 'or', label = 'R 3D Gsearch')
#         plt.title("For Stations with Vp err < {}\nVp/Vs over stations. RMS = {}".format(stdVp,RMS))
#         plt.ylabel("Vp/Vs")
#         plt.ylim((1.6, 2.0))
#         plt.setp( ax1.get_xticklabels(), visible=False)
#         plt.legend(loc=2)

#         ax1 = plt.subplot(212)
#         plt.plot(ns, Rk, 'ob', label = 'R Kanamori')
#         plt.plot(ns, Rdtr, 'or', label = 'R 3D Gsearch')
#         plt.title("Vp/Vs over stations with LINEAR regression detrend. RMS = {}".format(RMSdtr))
#         plt.ylabel("Vp/Vs")
#         plt.ylim((1.6, 2.0))
#         plt.xlabel("Station number")
#         plt.legend(loc=2)



#         # plt.figure(40)
#         # plt.subplot(211)
#         # ns = np.arange(len(Hk))
#         # # see http://matplotlib.org/examples/pylab_examples/subplots_demo.html
#         # plt.plot(ns, Hk, label = 'H Kanamori')
#         # plt.plot(ns, H, label = 'H', color = "red")
#         # plt.title("H over stations")
#         # plt.ylabel("H")
#         # plt.legend(loc=2)

#         # ax1 = plt.subplot(212)
#         # plt.plot(ns, Rk, label = 'R Kanamori')
#         # plt.plot(ns, R, label = 'R', color = "red")
#         # plt.title("R over stations")
#         # plt.ylabel("Vp/Vs")
#         # plt.legend(loc=2)


#         # plt.figure(50)

#         # # see http://matplotlib.org/examples/pylab_examples/subplots_demo.html
#         # ax1 = plt.subplot(311)
#         # plt.plot(Hk, R, '*', label = 'Vp/Vs')
#         # plt.title("Vp/Vs, Vp and Vs against KANAMORI crustal thickness H")
#         # plt.ylabel("Vp/Vs")
#         # plt.legend(loc=2)
#         # plt.setp( ax1.get_xticklabels(), visible=False)

#         # ax2 = plt.subplot(312, sharex = ax1)
#         # plt.plot(Hk, Vp, '*', label = 'Vp')
#         # plt.ylabel("Vp [km/s]")
#         # plt.legend(loc=2)
#         # plt.setp( ax1.get_xticklabels(), visible=False)

#         # ax3 = plt.subplot(313, sharex = ax1)
#         # plt.plot(Hk, Vs, '*', label = 'Vs')
#         # plt.xlabel("KANAMORI Crustal Thickness H [km]")
#         # plt.ylabel("Vs [km/s]")
#         # plt.legend(loc=2)


#     if "param" in plottype:

#         # Zero mean

#         ### Create vectors from raw data
#         R = np.array([x[1] for x in params])
#         Vp = np.array([x[2] for x in params])
#         H = np.array([x[3] for x in params])
#         Vs = 1 / R * Vp
#         R3 = np.array([x[4] for x in params])
#         Vp3 = np.array([x[5] for x in params])
#         H3 = np.array([x[6] for x in params])
#         Vs3 = 1 / R3 * Vp3
#         Rk = np.array([x[7] for x in params])
#         Hk = np.array([x[8] for x in params])

#         ns = np.arange(len(Hk))


#         plt.figure(num = 100 - i, figsize = (10, 10) )
#         #see http://matplotlib.org/examples/pylab_examples/subplots_demo.html
#         ax1 = plt.subplot(311)
#         plt.plot(H, R, 'ob', label = 'Vp/Vs Bostock')
#         plt.plot(H3, R3, 'or', label = 'Vp/Vs G3D')
#         plt.title("3D Grid search Vp/Vs, Vp and Vs against crustal thickness H")
#         plt.ylabel("Vp/Vs")
#         plt.legend(loc=2)
#         plt.setp( ax1.get_xticklabels(), visible=False)

#         ax2 = plt.subplot(312, sharex = ax1)
#         plt.plot(H, Vp, 'ob', label = 'Vp Bostock')
#         plt.plot(H3, Vp3, 'or', label = 'Vp G3D')
#         plt.ylabel("Vp [km/s]")
#         plt.legend(loc=2)
#         plt.setp( ax1.get_xticklabels(), visible=False)

#         ax3 = plt.subplot(313, sharex = ax1)
#         plt.plot(H, Vs, 'ob', label = 'Vs Bostock')
#         plt.plot(H3, Vs3, 'or', label = 'Vs G3D')
#         plt.xlabel("Crustal Thickness H [km]")
#         plt.ylabel("Vs [km/s]")
#         plt.legend(loc=2)


#         plt.figure(num = 213 - i, figsize = (10, 10) )

#         # see http://matplotlib.org/examples/pylab_examples/subplots_demo.html
#         ax1 = plt.subplot(211)
#         plt.plot(Rk ,R, 'ob', label = 'Kan & MB corr = {:.3}'.format( pearsonr(Rk, R)[0] ) )
#         plt.plot(Rk, R3, 'or', label = 'Kan & 3D corr = {:.3}'.format( pearsonr(Rk, R3)[0] ) )
#         plt.title("Correlation between Vp/Vs")
#         plt.ylabel("Vp/Vs")
#         plt.xlabel("Vp/Vs Kanamori")
#         plt.legend(loc=2)
#         #plt.setp( ax1.get_xticklabels(), visible=False)

#         ax1 = plt.subplot(212)
#         plt.plot(Hk ,H, 'ob', label = 'Kan & MB corr = {:.3}'.format( pearsonr(Hk, H)[0] ) )
#         plt.plot(Hk, H3, 'or', label = 'Kan & 3D corr = {:.3}'.format( pearsonr(Hk, H3)[0] ) )
#         plt.title("Correlation between H")
#         plt.ylabel("H")
#         plt.xlabel("H Kanamori")
#         plt.legend(loc=2)

#         pp.savefig()

#         plt.figure(num = 133 - i, figsize = (10, 10) )
#         # see http://matplotlib.org/examples/pylab_examples/subplots_demo.html
#         ax1 = plt.subplot(411)
#         plt.plot(R ,R3, 'ob', label = '3D & MB corr = {:.3}'.format( pearsonr(R, R3)[0] ) )
#         plt.title("Correlation between Bostock and 3D grid parameters")
#         plt.ylabel("R 3D")
#         plt.xlabel("R Bostock")
#         plt.legend(loc=2)

#         ax1 = plt.subplot(412)
#         plt.plot(Vp ,Vp3, 'ob', label = '3D & MB corr = {:.3}'.format( pearsonr(Vp, Vp3)[0] ) )
#         plt.ylabel("Vp 3D")
#         plt.xlabel("Vp Bostock")
#         plt.legend(loc=2)

#         ax1 = plt.subplot(413)
#         plt.plot(Vs ,Vs3, 'ob', label = '3D & MB corr = {:.3}'.format( pearsonr(Vs, Vs3)[0] ) )
#         plt.ylabel("Vs 3D")
#         plt.xlabel("Vs Bostock")
#         plt.legend(loc=2)

#         ax1 = plt.subplot(414)
#         plt.plot(H ,H3, 'ob', label = 'Kan & MB corr = {:.3}'.format( pearsonr(H, H3)[0] ) )
#         plt.ylabel("H 3D")
#         plt.xlabel("H Bostock")
#         plt.legend(loc=2)

#         pp.savefig()


# corrR = np.zeros(51)
# corrVp = np.zeros(51)
# corrVs  = np.zeros(51)
# corrH = np.zeros(51)
# corrRRk = np.zeros(51)
# corrHHk = np.zeros(51)
# corrR3Rk = np.zeros(51)
# corrH3Hk = np.zeros(51)

# for i in range(50, 10, -1):

#     stdVp[i] = 0.01*i
#     args = Args()
#     args.addQuery("stdVp","lte", str(stdVp[i]) )
#     #args.addKeys()
#     stdict = queryStats(stdict, args)
#     #getStats(stdict, args, printer = True)

#     ### Create data
#     params = []
#     #g3_mb = []
#     for key, value in stdict.items():
#         if key in stdict:
#             params.append(  (key, value['R'], value['Vp'], value['H'], g3d[key]['R'], g3d[key]['Vp'], g3d[key]['H'], kand[key]['R'], kand[key]['H']) )



#        ### Create vectors from raw data
#     R = np.array([x[1] for x in params])
#     Vp = np.array([x[2] for x in params])
#     H = np.array([x[3] for x in params])
#     Vs = 1 / R * Vp
#     R3 = np.array([x[4] for x in params])
#     Vp3 = np.array([x[5] for x in params])
#     H3 = np.array([x[6] for x in params])
#     Vs3 = 1 / R3 * Vp3
#     Rk = np.array([x[7] for x in params])
#     Hk = np.array([x[8] for x in params])

#     ns = np.arange(len(Hk))

#     corrVp[i] =  pearsonr(Vp, Vp3)[0]
#     corrR[i] =  pearsonr(R, R3)[0]
#     corrVs[i] =  pearsonr(Vs, Vs3)[0]
#     corrH[i] =  pearsonr(H, H3)[0]
#     corrRRk[i] =   pearsonr(Rk, R)[0]
#     corrHHk[i] =   pearsonr(Hk, H)[0]
#     corrR3Rk[i] =   pearsonr(Rk, R3)[0]
#     corrH3Hk[i] =   pearsonr(Hk, H3)[0]


# plt.figure(num = 1000, figsize = (10, 10) )
# # see http://matplotlib.org/examples/pylab_examples/subplots_demo.html
# plt.subplot(211)
# plt.plot(stdVp ,corrR, 'b', label = 'Vp/Vs corr')
# plt.plot(stdVp ,corrVp, 'r', label = 'Vp corr')
# plt.plot(stdVp ,corrVs, 'g', label = 'Vs corr')
# plt.plot(stdVp ,corrH, 'k', label = 'H corr')
# plt.title("Correlation between Bostock & 3Dgsearch as a function of Vp error")
# plt.ylabel("correlation Coeffs")
# plt.xlabel("Vp Bootstrap Error")
# plt.xlim( (0.1, 0.5) )
# plt.ylim( (0.3, 1.1) )
# plt.legend(loc=2)

# plt.subplot(212)
# plt.plot(stdVp ,corrRRk, 'b', label = 'R Bostock vs R Kanamori corr')
# plt.plot(stdVp ,corrR3Rk, 'r', label = 'R 3D vs R Kanamori corr')
# plt.plot(stdVp ,corrHHk, 'g', label = 'H Bostock vs H kanamori corr')
# plt.plot(stdVp ,corrH3Hk, 'k', label = 'H 3D vs H kanamori corr')
# plt.title("Correlation between Bostock & Kan & 3Dalg & Kan as a function of Vp error")
# plt.ylabel("correlation Coeffs")
# plt.xlabel("Vp Bootstrap Error")
# plt.xlim( (0.1, 0.5) )
# plt.ylim( (0.0, 1.1) )
# plt.legend(loc=2 ,prop={'size':10} )


# pp.savefig()
# pp.close()
# plt.show()


    ##### Geochronology Plots
    # if "geochron" in plottype:
    #     ### Create vectors from raw data
    #     H = np.array([x[3] for x in geodata])
    #     R = np.array([x[1] for x in geodata])
    #     Vp = np.array([x[2] for x in geodata])
    #     rng = np.array([x[4] for x in geodata])
    #     Vs = 1 / R * Vp

    #     plt.figure(2)
    #     ax1 = plt.subplot(111)
    #     plt.hlines(y = H, xmin = rng[:,1], xmax = rng[:,0])
    #     plt.title("Crustal Thickness H against Bedrock Age in Mya")
    #     plt.ylabel("Crustal Thickenss [km]")
    #     #plt.setp( ax1.get_xticklabels(), visible = False)
    #     ax1.set_xlim(ax1.get_xlim()[::-1])


    #     #ax2 = plt.subplot(212, sharex = ax1)
    #     #plt.hlines(y = Vs, xmin = rng[:,1], xmax = rng[:,0])
    #     plt.xlabel("Million Years Ago")
    #     #plt.ylabel("Shear Wave Velocity Vs [km/s]")
