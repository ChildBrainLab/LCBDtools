# TODO: want path appends to be done in
# venv, so can import modules correctly
# and not using relative paths that may change
# in future releases
import sys
sys.path.append('../../..')

# LCBD modules
from preprocessing.scripts import argParser
from preprocessing.src import Plots

import os, shutil
from os.path import join
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

import mne
import mne_nirs

args = argParser.main([
    "data_folder",
    # "run",
    # "ex_subs",
    "participant_num_len"
])

studyDir = args.data_folder

subjects = [sub for sub in os.listdir(studyDir)]
# print(subjects)

sessions = []
for subject in subjects:
    for visit in os.listdir(join(studyDir, subjects)):
        sessions.append(join(studyDir, subject, visit))

print(sessions)

quit()


participant_data_paths = []
for session in sessions:
    participant_data_paths.append([join(session, participant) for \
        participant in os.listdir(session)])




fnames = [join(studyDir, subj, )]

# set defaults for mne viz to use pyvista 3d backend
# mne.viz.set_3d_backend("pyvista")

fnirs_data_folder = mne.io.read_raw_nirx(fname)
