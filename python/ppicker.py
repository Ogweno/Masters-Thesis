#!/usr/bin/python2
#
# python-mode indent C-c < or C-c >
# python-mode comment/uncomment region M-;
# Note Scipy detrend is same as doing a remove mean and then detrend
# Detrend demean taper rotate rename save

###########################################################################
# IMPORTS
###########################################################################
import os, re, time, shutil, sys
from preprocessor import SeisDataError
from loopApplyDRIVER import renameEvent, is_number
import matplotlib.pyplot as plt
from obspy.core import read
import numpy as np

def ppicker(eventdir,pname,sname):
    """ Function ppicker is a ginput based arrival picker
    allowing for 3 time picks which are saved in SAC data headers"""
    
    pf = os.path.join(eventdir, pname)
    sf = os.path.join(eventdir, sname)
    pt = read(pf)[0]
    st = read(sf)[0]
    p, s = (pt.data, st.data)

    dt = pt.stats.delta
    N = len(pt.data)
    b = pt.stats.sac['b']
    depth = pt.stats.sac['evdp']
    t0 = (pt.stats.sac['t0'] - b ) / dt       
    t4 = (pt.stats.sac['t4'] - b ) / dt   
    t7 = (pt.stats.sac['t7'] - b ) / dt
    left = round(t0 - 20/dt)
    right = round(t0 + 240/dt)
    t = np.around(np.arange(-t0*dt,(N - t0)*dt,dt))
    nn = np.arange(0,N)

    while True:
    #plt.subplot(2,1,1)
        print "Pick P-coda. Begin then End on event:", eventdir
        plt.figure( num = None, figsize = (22,6) )
        plt.plot(p, label = 'Pcomp')
        plt.xticks(nn[::200],t[::200])
        plt.title('{} \n P-trace, source depth = {}'.format( eventdir, depth) )
        plt.axvline(x = t0, color = 'y', label = 'gett P')
        plt.axvline(x = t4, color = 'g', label = 'gett pP')
        plt.axvline(x = t7, color = 'r', label = 'gett PP')
        plt.xlim(left, right)
        plt.xlabel('Time \n P arrival is zero seconds')
        plt.legend()
        # GINPUT b1 = add point |  b2 = STOP |  b3 = delete point
        x = plt.ginput(n = 2, timeout = 0, show_clicks = True)
        try:
            T1 = x[0][0]*dt + b
            T3 = x[1][0]*dt + b
        except IndexError:
            print "Not all picks made in", eventdir
            print "Please retry the picks"
            continue
        plt.close()

        inp = raw_input("Keep trace? 'y' for yes, 'n' for no, 'r' for redo: ")
        if 'r' in inp:
            continue
        if 'y' in inp:
            pt.stats.sac['t1'] = T1
            pt.stats.sac['t3'] = T3
            pt.write(pf, format='SAC')
            st.stats.sac['t1'] = T1
            st.stats.sac['t3'] = T3
            st.write(sf, format='SAC')
            return
        elif 'n' in inp:
            raise poorDataError('Data was discarded as poor')
    #plt.subplot(2,1,2)
    #plt.plot(s)
    #plt.title('S-trace')
    #plt.show()

if __name__== '__main__' :
    

    if (len(sys.argv) != 2):
        print "Send a absolute directory"
        exit()
        
    evdir = sys.argv[1]
    reg2 = re.compile(r'^stack_(\w)\.sac')
    events = os.listdir(evdir)
    for event in events:
        if not is_number(event): # Make sure event dir is right format, skip those not in number format
            continue
        comps = []
        eventdir = os.path.join(evdir,event)
        files = os.listdir(eventdir)
        for fs in files:
            m = reg2.match(fs)
            if m:
                comps.append((m.group(1),fs))
 
    ###########################################################################
    # Check if three components have been found
    # If yes, sopt alphebetically and call processor function
    ###########################################################################
        if (len(comps) != 2):
             print "Did not register 2 components in directory:", eventdir
             renameEvent(eventdir,"MissingComponents")
             continue
         # Sort in decending alphabetical, so 'E' is [0] 'N' is [1] and 'Z' is [2]
         # Pull out sacfiles from zipped sorted list.
        comps.sort()
        _ , sacfiles = zip(*comps)

        try:
            ppicker(eventdir,sacfiles[0],sacfiles[1])

        except SeisDataError as e:    
            renameEvent(eventdir, e.msg)
            continue
