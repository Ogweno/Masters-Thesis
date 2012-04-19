#!/usr/bin/python2
#
# python-mode indent C-c < or C-c >
# python-mode comment/uncomment region M-;
# Note Scipy detrend is same as doing a remove mean and then detrend
# Detrend demean taper rotate rename save

###########################################################################
# IMPORTS
###########################################################################
from obspy.core import read
from obspy.signal.rotate import rotate_NE_RT as rotate 
from scipy.signal.signaltools import detrend
from obspy.signal.invsim import cosTaper
import numpy as np
import os.path

###########################################################################
#  SET UTILS, VARS
###########################################################################



###########################################################################
# preprocess function to be imported by program which walks through
# directories and applies this function.
# This does Demean, Detrend, taper, and rotation.
# It expects 3 SAC files in component order: E,N,Z. (passed as tuple)
# It saves the rotated files into eventdir
###########################################################################
def preprocess(eventdir, sacfiles):
    """preprocess performs the demean,detrend,taper and rotation into radial and
    transverse components. It saves these at STACK_R.sac and STACK_T.sac"""
    
    ev = []
    
    # READ 3 Component SAC files into object array.
    for i in range(3):
        ff = os.path.join(eventdir, sacfiles[i])
        st = read(ff)
        ev.append(st[0]) 

    # Detrend and taper all three components
    for i in range(3):
        ev[i].data = detrend(ev[i].data) # Detrend all components
        ctap = cosTaper(len(ev[i].data))
        ev[i].data = ev[i].data * ctap

    # Rotate to E and N to R and T
    baz = ev[0].stats.sac['baz']
    # Note R, T = rotate(N, E) 
    ev[1].data, ev[0].data = rotate(ev[1].data, ev[0].data,baz)


    # Save transformed data objects
    ev[0].write(os.path.join(eventdir,'STACK_T.sac'), format='SAC')
    ev[1].write(os.path.join(eventdir,'STACK_R.sac'), format='SAC')
    ev[2].write(os.path.join(eventdir,'STACK_Z.sac'), format='SAC')

    




