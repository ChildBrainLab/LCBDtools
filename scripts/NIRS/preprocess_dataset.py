# General dependencies
import os, shutil
from os.path import join
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from copy import deepcopy
from glob import glob
from itertools import compress

import mne
import mne_nirs

# LCBD dependencies
# add relative path to our toolbox
# TODO: want path appends to be done in
# venv, so can import modules correctly
# and not using relative paths that may change
# in future releases
import sys
sys.path.append('../../')
from LCBDtools.scripts import argParser
from LCBDtools.src import Plots

args = argParser.main([
    "data_folder",
    "task_folder",
    "run",
    "participant_num_len",
    "ex_subs",
    "in_subs",
    "output_dir",
    "covariates"
])

# Some configuration variables
nirs_dirs = args.data_folder
task_dir = args.task_folder
participant_num_len = args.participant_num_len
ex_subs = args.ex_subs # any subjects to not include in the dataset
in_subs = args.in_subs # limit inclusion to these subjects
output_dir = args.output_dir
covariates = args.covariates # read covariates from a csv file
if covariates is not None:
    covariates = pd.read_csv(covariates)

# bit so that ex_subs and in_subs are more flexible:
# they can be a typed list of subject numbers
# or else they can be a '\n'-separated text file of subject numbers
for i, lst in enumerate([ex_subs, in_subs]):
    # CL argument is empty
    if len(lst) < 1:
        continue
    # CL argument is not a file (assume it is string list)
    elif not os.path.isfile(lst[0]):
        continue
    # CL argument is filepath to txt
    else:
        with open(lst[0]) as f:
            if i == 0:
                ex_subs = [sub.split()[0] for sub in f.readlines()]
                f.close()
            elif i == 1:
                in_subs = [sub.split()[0] for sub in f.readlines()]
                f.close()

### GATHER SESSIONS ###
##############################

# get all matching session dirs with subject in top level of glob
session_dirs = [d for d in glob(study_dir+"/*/*{}".format(run))]

# use exclusion / inclusion switch
if len(in_subs) > 0:
    session_dirs = [d for d in session_dirs if d in in_subs]
elif len(ex_subs) > 0:
    session_dirs = [d for d in session_dirs if d not in ex_subs]

# subjects are top level folders in the study_dir that have
# session folders with this run
subjects = [d.strip(study_dir).split('/')[0] for d in session_dirs]

# assum participant_num_len from first item, if not set
if participant_num_len is None:
    participant_num_len = len(subjects[0])

### PROCESS EACH SESSION WITH MNE ###
#####################################
for i, ses in enumerate(session_dirs):

    # meta data
    ################################
    subject = subjects[i]

    # load mne.io.Raw objects
    try:
        raw = mne.io.read_raw_nirx(ses).load_data()
    except:
        print("Failure to load, skipping:", ses)
        continue

    # if covariates file is available, load its series for the subject
    if covariates is not None:
        idx = covariates[covariates['subject'] == str(subject)].index
        if len(idx) == 0:
            print("Subject not found in covariates file.")
            print("Skipping:", ses)
            continue

        elif len(idx) > 1:
            print("Subject is duplicated in covariates file.")
            print("Skipping:", ses)
            continue

        else:
            metaSeries = []
            metaCols = []

            for col in [col for col in df.columns if "subject" != col]:
                metaSeries.append(df.iloc[idx[0]][col])
                metaCols.append(col)

    # if task data is available, load it as an object
    if task_dir is not None:
        task_fnames = glob(join(task_dir+"/{}/*{}*.csv".format(
            subject, run)))

        if len(task_fnames) == 0:
            print("No task data found for this participant.")
            print("Failure to find task data, skipping:", ses)
            continue

        elif len(task_fnames) > 1:
            print("Too many task data found for this participant.")
            print("Failure to find task data, skipping:", ses)
            continue

        task_fname = task_fnames[0]

        # switch for run type? to pick which loader?
        if run.lower() == "flanker":
            from LCBDtools.Stimuli.Flanker import TaskReader
            try:
                flanker_series = TaskReader(task_fname).flankerSeries
                task_sub = os.path.basename(task_fname)[:participant_num_len]
                if subject != task_sub:
                    print("Warning. Task file may be named incorrectly.")
                    print("See:", task_fname)

                for flank in flanker_series:
                    # evaluate flanker data and assign meta data?
                    flank.eval()
                    # add covariate data into flank object (because)
                    if covariates is not None:
                        for j, col in enumerate(metaCols):
                            flank.meta[col] = metaSeries[j]
            except:
                print("Problem encountered when loading Flanker data.")
                print("Failure, skipping:", ses)
                continue

    
