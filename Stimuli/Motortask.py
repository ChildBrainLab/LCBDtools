import sys

import os, shutil
import numpy as np
import math, scipy
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from math import floor

sys.path.append('../..')

from LCBDtools.src.TimeSeries import TimeSeries

class MotorTS:
    """
    Object which stores time series of single trial type  of Motor task. I.e.,
    stimulus type, block's on/off,

    :param times: onset / offset times relative to t=0 in seconds
    :type times: list of tuples
    """

    def __init__(self, times, samplerate, refstart=0, refstop=None):
        self.times = [(float(time[0]), float(time[1])) for time in times]
        self.refstart = refstart
        if refstop is None:
            self.refstop = times[-1][1]
        else:
            self.refstop = refstop
        self.samplerate = samplerate

    def get_TS(self):

        total = floor(float(self.refstop) - float(self.refstart))

        time = np.linspace(
            0,
            total,
            num=floor(total*self.samplerate))

        sig = np.zeros(time.shape)
        for stim in self.times:
            start = stim[0] - self.refstart
            stop = stim[1] - self.refstart

            locs = np.where((time > start) & (time < stop))
            sig[locs] = 1

        return TimeSeries(sig, time=time, sampleRate=self.samplerate)
            

class TaskReader:
    """
    Object used to read data from an LCBD PsychoPy Flanker session. Specifically,
    this object was built for the output from Version 3 of P-CAT Flanker task.
    It should be adapated as needed to suit further task developments.

    :param path: relative path to data file from the working directory
    :type path: str
    """
    def __init__(self, path, defaultLength=226):
        self.path = path

        # return tuple of filename and file extension
        fname, fext = os.path.splitext(path)

        if fext == ".csv":
            WS = pd.read_csv(self.path, sep=",", low_memory=False)
        elif fext == ".tsv":
            WS = pd.read_csv(self.path, sep="\t", low_memory=False)
        elif fext == ".xlsx":
            WS = pd.read_excel(self.path)

        try:
            # read all required / expected metadata
            try:
                self.participant = str(int(WS['participant'][0]))
            except:
                self.participant = str("None")
            self.session = int(WS['session'][0])
            self.date = datetime.strptime(
                str(WS['date'][0]),
                '%Y_%b_%d_%H%M')

            self.sampleRate = float(WS['frameRate'][0])

        except (UnboundLocalError, KeyError) as e:
            print("Error: an incorrect key was not found during"
            " the loading of some files and they will be skipped.")
            print("Loading: ", self.path)

        # get scan start time (in seconds)
        scan_start = float(WS['wait2.started'][1])

        # image: tongue
        # image_2: RH
        # image_3: RF
        # image_4: LH
        # image_5: LF
        stim_keys = {
            'tongue': 'image',
            'RH': 'image_2',
            'RF': 'image_3',
            'LH': 'image_4',
            'LF': 'image_5'}

        stims = {}
    
        for stim, col in stim_keys.items():
            stimstarts = WS[WS[col+'.started'].notnull()][col+'.started'].tolist()
            stimstops = WS[WS[col+'.stopped'].notnull()][col+'.stopped'].tolist()
            #stimstarts.replace('', np.nan, inplace=True)
            #stimstops.replace('', np.nan, inplace=True)
            #stimstarts = stimstarts.dropna(inplace=True)
            #stimstops = stimstops.dropna(inplace=True)

            stims[stim] = tuple(zip(
                stimstarts,
                stimstops))

        """
        scan_stop = 0
        for stim, times in stims.items():
            for time in times:
                if time[1] > scan_stop:
                    scan_stop = time[1]
        defaultLength = scan_stop
        """
        for stim, times in stims.items():
            ts = MotorTS(
                times,
                float(1/1.1),
                refstart=scan_start,
                refstop=float(defaultLength+scan_start))
            ts = ts.get_TS()
            
            #print(ts.signal.shape)
            #print(ts.time[-1])

            #from scipy.signal import resample
            #newsig = resample(ts.signal, 205)
            #newtime = resample(ts.time, 205)

            #ts.interpol_resample(sample_rate=float(1/1.1))
            
            np.savetxt(self.path.replace(".csv", "") + "_{}_ts.txt".format(stim), ts.signal, fmt='%i')
