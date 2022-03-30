"""
Takes data folder as a "clean" path of hyperscanning data?
Currently anticipating CARE format, although it should probably be set up
to find the parent folders of any globbed .nirx formatted directories instead,
because this will not work for any configuration of visit / parent / child
interaction data. TODO ^ >> now may be fixed
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
sys.path.append('../../..')
from preprocessing.scripts import argParser
from preprocessing.src import Plots

args = argParser.main([
    "data_folder",
    # "run",
    "ex_subs",
    "participant_num_len"
])

# Some configuration variables
study_dir = args.data_folder
# default length of participant numbers
participant_num_len = args.participant_num_len
ex_subs = args.ex_subs # any subjects to not include in the dataset

# session_dirs = [d for d in glob(study_dir+"/*/V*/*fNIRS") \
#     if os.path.basename(os.path.split(os.path.split(d)[1])[1]) not in ex_subs]

session_dirs = [os.path.split(d)[0] for d in glob(
    study_dir+"**/*_probeInfo.mat",
    recursive=True) \
    if d.strip(study_dir).strip("/")[:participant_num_len] not in ex_subs]

subjects = list(set([os.path.basename(d)[:participant_num_len] for \
    d in session_dirs]))

mne.viz.set_3d_backend('pyvista')
raw_intensities = []

print("Processing:")
print("================")
for ses in tqdm(session_dirs):
    # if (os.path.basename(ses) != "50430_V1_fNIRS") and (os.path.basename(ses) != "50431_V1_fNIRS"):
    #     continue
    try:
        # print("Working sessions:", ses)
        raw_intensity = mne.io.read_raw_nirx(ses, verbose=False).load_data(
            verbose=False)
        # raw_intensities[-1].resample(0.7) # downsample to 0.7 HZ to run faster

        # plot sensors and save to session dir
        fig = raw_intensity.plot_sensors(
            kind='topomap',
            show_names=True,
            to_sphere=True,
            show=False)
        plt.savefig(join(ses, 'fig_sensors.png'))
        # plt.close()

        # cleaning up annotations before analysis (for boxcar plot too?)
        # raw_ints.rename({
        #     '1.0': 'Pyschopy Trigger',
        #     '4.0': 'Other Psychopy Trigger?',
        #     '8.0': 'Manual Trigger'})
        #
        # raw_ints.annotations.delete(raw_ints.annotations.description == '15.0')
        #
        # raw_ints.annotations.set_durations(5)

        # plot what MNE assumes the events to be (from the NIRStar file)
        # and save to session dir
        events, event_dict = mne.events_from_annotations(
            raw_intensity, verbose=False)
        fig = mne.viz.plot_events(
            events,
            event_id=event_dict,
            sfreq=raw_intensity.info['sfreq'],
            show=False)
        plt.savefig(join(ses, 'fig_events.png'))
        # plt.close()

        # plot what MNE assumes the events to be (from the NIRStar file)
        # as a BOXCAR plot this time
        # and save to session dir
        # s = mne_nirs.experimental_design.create_boxcar(raw_intensity)
        #
        # fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(30, 6))
        # plt.plot(raw_intensity.times, s, axes=axes)
        # plt.legend(["?", "??"], loc="upper right")
        # plt.xlabel("Time (s)")
        # plt.ylabel("Stimulus")
        # plt.title("Trial Events for Subject {}".format(
        #     raw_intensity.info.subject_info['id']))
        # # plt.xlim(0, 1200)
        # plt.savefig(join(ses, 'fig_boxcar.png'))
        # plt.close()
    except:
        print("Failure:", ses)
