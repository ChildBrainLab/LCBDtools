"""
Takes data folder as a "clean" path of hyperscanning data?
Currently anticipating CARE format, although it should probably be set up
to find the parent folders of any globbed .nirx formatted directories instead,
because this will not work for any configuration of visit / parent / child
interaction data. TODO ^ >> now may be fixed, check with eDOC / etc.
"""

# General dependencies
import os, shutil
from os.path import join
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
# import pandas as pd
# import seaborn as sns
# from copy import deepcopy
from glob import glob

import mne
import mne_nirs

from mne_nirs.experimental_design import make_first_level_design_matrix
from mne_nirs.statistics import run_glm
from mne_nirs.channels import (
    get_long_channels,
    get_short_channels,
    picks_pair_to_idx)

from nilearn.plotting import plot_design_matrix

# LCBD dependencies
# add relative path to our toolbox
# TODO: want path appends to be done in
# venv, so can import modules correctly
# and not using relative paths that may change
# in future releases
import sys
sys.path.append('../../../..')
from LCBDtools.scripts import argParser
from LCBDtools.src import Plots

def create_boxcar(raw, event_id=None, stim_dur=1):
    """
    Generate boxcar representation of the experimental paradigm.

    Parameters
    ----------
    raw : instance of Raw
        Haemoglobin data.
    event_id : as specified in MNE
        Information about events.
    stim_dur : Number
        The length of your stimulus.

    Returns
    -------
    s : array
        Returns an array for each annotation label.
    """
    from scipy import signal
    
    events, ids = mne.events_from_annotations(
        raw,
        event_id=event_id,
        verbose=False)
    
    s = np.zeros((len(raw.times), len(ids)))
    for idx, id in enumerate(ids):
        bc = signal.boxcar(round(raw.info['sfreq'] * stim_dur[id]))
        
        id_idx = [e[2] == idx + 1 for e in events]
        id_evt = events[id_idx]
        event_samples = [e[0] for e in id_evt]
        s[event_samples, idx] = 1.
        s[:, idx] = np.convolve(s[:, idx], bc)[:len(raw.times)]
    return s

args = argParser.main([
    "data_folder",
    # "run",
    "participant_num_len",
    "ex_subs",
    "in_subs",
])

# Some configuration variables
nirs_dir = args.data_folder
participant_num_len = args.participant_num_len # default length of participant numbers
ex_subs = args.ex_subs # any subjects to not include in the dataset
in_subs = args.in_subs # limit inclusion to these subjects

# all sessions that meet naming conventions
session_dirs = [os.path.split(d)[0] for d in glob(
    nirs_dir+"**/*_probeInfo.mat",
    recursive=True) \
    if d.strip(nirs_dir).strip("/")[:participant_num_len] not in ex_subs]

# generate list of subjects
subjects = list(set([os.path.basename(d)[:participant_num_len] for \
    d in session_dirs]))

# only include subs in 'in_subs', if given
if in_subs is None:
    in_subs = subjects
else:
    session_dirs = [ses for ses in session_dirs \
        if ses.strip(nirs_dir).strip("/")[:participant_num_len] in in_subs]

if len(session_dirs) == 0:
    print("No session directories were considered valid.")
    sys.exit(3)

mne.viz.set_3d_backend('pyvista')
raw_intensities = []

print("Generating Session Info:")
print("================")
for ses in tqdm(session_dirs):
    # if (os.path.basename(ses) != "50430_V1_fNIRS") and (os.path.basename(ses) != "50431_V1_fNIRS"):
    #     continue
    evts = glob(ses + "/*.evt")
    if len(evts) != 2:
        print("There should be 2 evt files. Skipping:", os.path.basename(ses))
        continue
    else:
        # print("Working sessions:", ses)
        raw_intensity = mne.io.read_raw_nirx(ses, verbose=False).load_data(
            verbose=False)
        # raw_intensities[-1].resample(0.7) # downsample to 0.7 HZ to run faster

        # skip this ses if data < 10000 samples
        if len(raw_intensity) < 10000:
            print("Session too short. Skipping:", ses)
        
        # plot sensors and save to session dir
        fig = raw_intensity.plot_sensors(
            kind='topomap',
            show_names=True,
            to_sphere=True,
            show=False)
        plt.savefig(join(ses, 'fig_sensors.png'))
        plt.clf()

        # cleaning up annotations before analysis (for boxcar plot too?)

        # plot what MNE assumes the events to be (from the NIRStar file)
        # and save to session dir

        try:
            raw_intensity.annotations.rename({
                '1.0': 'Block 1 Start',
                '2.0': 'Block 2 Start',
                '4.0': 'Block 3 Start',
                '128.0': 'Stop Signal'})

            durations = {
                'Block 1 Start': 120,
                'Block 2 Start': 105,
                'Block 3 Start': 120,
                'Stop Signal': 1}
        except:
            print("The annotations are not as expected, skipping:", ses)
            continue
        
        raw_intensity.annotations.set_durations(durations, verbose=True)
        
        events, event_dict = mne.events_from_annotations(
            raw_intensity, verbose=False)
        
        fig = mne.viz.plot_events(
            events,
            event_id=event_dict,
            sfreq=raw_intensity.info['sfreq'],
            show=False)
        
        plt.savefig(join(ses, 'fig_events.png'))
        plt.close()

        # plot what MNE assumes the events to be (from the NIRStar file)
        # as a BOXCAR plot this time
        # and save to session dir
        
        try:
            s = create_boxcar(
                raw_intensity,
                stim_dur = durations)
        except:
            print("Error creating boxcar signal for session:", ses, ", skipping.")
            continue
    
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(15, 6))
        plt.plot(raw_intensity.times, s, axes=axes)
        plt.legend([
            "Block 1 Start",
            "Block 2 Start",
            "Block 3 Start"],
            loc="upper right")
        plt.xlabel("Time (s)")
        plt.ylabel("Stimulus")
        plt.title(raw_intensity.info['subject_info']['his_id'])
#         plt.xlim(0, 1800)
        plt.savefig(join(ses, 'fig_boxcar.png'))
        plt.close()

