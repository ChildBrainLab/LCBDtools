# General dependencies
import os, shutil, matplotlib
from os.path import join
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from copy import deepcopy
from glob import glob
from itertools import compress

import mne
import mne_nirs

import sys

from LCBDtools.src import argParser
from LCBDtools.src import Plots


class processor:

	def __init__(self):

	def load(self, ses):
	    try:
	        raw = mne.io.read_raw_nirx(ses).load_data()
	    except:
	        print("Failure to load, skipping:", ses)
	        continue

	def preprocess(self, raw):
		try:
		    data = raw.copy()

		    # convert to optical density
		    raw_od = mne.preprocessing.nirs.optical_density(data)

		    # scalp coupling index
		    sci = mne.preprocessing.nirs.scalp_coupling_index(raw_od)
		    raw_od.info['bads'] = list(compress(raw_od.ch_names, sci < 0.5))

		    # temporal derivative distribution repair (motion)
		    tddr_od = mne.preprocessing.nirs.tddr(raw_od)

		    # haemoglobin conversion
		    haemo = mne.preprocessing.nirs.beer_lambert_law(tddr_od, ppf=0.1)

		    # mark bad channels if bad channel df supplied
		    # bad_channels_dict
		    if bad_channels_dict is not None:
		        if subject in bad_channels_dict.keys():
		            for ch in bad_channels_dict[subject]:
		                if ch not in haemo.info['bads']:
		                    haemo.info['bads'].append(ch)

		    # bandpass filter
		    haemo_bp = haemo.copy().filter(
		        0.05, 0.7, h_trans_bandwidth=0.2, l_trans_bandwidth=0.02)

		    data = haemo_bp.copy()

		except:
		    print("Something went wrong during preprocessing.")
		    print("Skipping:", ses)
		    continue

	def save(self):
	    try:
	        sespath = ses.strip(nirs_dir)
	        outpath = os.path.join(output_dir, sespath)

	        # if output_dir does not exist, make it
	        if not os.path.isdir(output_dir):
	            os.mkdir(output_dir)

	        tempfolder = ""
	        for folder in sespath.split('/'):
	            tempfolder += folder
	            tempfolder += "/"
	            if not os.path.isdir(os.path.join(output_dir, tempfolder)):
	                os.mkdir(os.path.join(output_dir, tempfolder))

	        outpath = outpath + "/{}_{}.fif".format(str(subject), task.lower())

	    except:
	        print("Something went wrong when generating the output path name.")
	        print("Skipping:", ses)
