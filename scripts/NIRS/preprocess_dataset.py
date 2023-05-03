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

# LCBD dependencies
# add relative path to our toolbox
# TODO: want path appends to be done in
# venv, so can import modules correctly
# and not using relative paths that may change
# in future releases
import sys
sys.path.append('../../..')
from LCBDtools.src import argParser
from LCBDtools.src import Plots

args = argParser.main([
    "data_folder",
    "task_folder",
    "task",
    "participant_num_len",
    "ex_subs",
    "in_subs",
    "output_dir",
    "covariates",
    "bad_channels",
    "verbose",
    "force"
])

# Some configuration variables
nirs_dir = args.data_folder
task_dir = args.task_folder
participant_num_len = args.participant_num_len
task = args.task
ex_subs = args.ex_subs # any subjects to not include in the dataset
in_subs = args.in_subs # limit inclusion to these subjects
output_dir = args.output_dir
covariates = args.covariates # read covariates from a csv file
bad_channels = args.bad_channels
verbose = args.verbose

if covariates is not None:
    covariates = pd.read_csv(covariates)
if bad_channels is not None:
    import json
    f = open(bad_channels, 'r')
    bad_channels_dict = json.load(f)
    f.close()

# bit so that ex_subs and in_subs are more flexible:
# they can be a typed list of subject numbers
# or else they can be a '\n'-separated text file of subject numbers
for i, lst in enumerate([ex_subs, in_subs]):
    # CL argument is empty
    if lst is None:
        continue
    elif lst == []:
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
if in_subs is None:
    in_subs = []
if ex_subs is None:
    ex_subs = []

### GATHER SESSIONS ###
##############################

# get all matching session dirs with subject in top level of glob
session_dirs = glob(nirs_dir+"*/*/*/")
nirs_dir_len = len(nirs_dir)
session_dirs = [d[nirs_dir_len:] for d in session_dirs]


# use exclusion / inclusion switch
if len(in_subs) > 0:
    session_dirs = [d for d in session_dirs if d[:5] in in_subs]
elif len(ex_subs) > 0:
    session_dirs = [d for d in session_dirs if d[:5] not in ex_subs]

# subjects are top level folders in the study_dir that have
# session folders with this run
subjects = [d.split('/')[0] for d in session_dirs]

# assum participant_num_len from first item, if not set
if participant_num_len is None:
    participant_num_len = len(subjects)

if verbose is True:
    print("Session dirs:", session_dirs)

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
        task_fnames = glob(join(task_dir+"/{}/*{}*/*{}*.csv".format(
            subject, task, task.lower())))

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
        if task.lower() == "flanker":
            from LCBDtools.Stimuli.Flanker import TaskReader
            try:
                # load Flanker Object from psychopy file
                flanker_series = TaskReader(task_fname).flankerSeries
                task_sub = os.path.basename(task_fname)[:participant_num_len]
                if subject != task_sub:
                    print("Warning. Task file may be named incorrectly.")
                    print("See:", task_fname, "with session", ses)

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

            durations = {
                'Directional': 63,
                'Indirectional': 31.5}

            # this is the joining of the Flanker psychopy information
            # into the MNE raw object
            try:
                events, event_dict = mne.events_from_annotations(
                    raw,
                    verbose=False)

                if len(events) == 20:
                    pass

                elif len(events) == 21:
                    raw.annotations.delete(0)

                elif len(events) == 11:
                    print("Weird session with 11 flanks. Unsure how to proceed.")
                    print("Skipping:", ses)
                    continue

                else:
                    print("Unfamiliar number of events. Skipping:", ses)
                    continue

                # clean up so we only have starts (fixation)
                # by deleting every 2nd index from annotations
                raw.annotations.delete([
                    range(1, len(raw.annotations), 2)])

                # rename and set durations for each
                # 315 seconds total for directional,
                # 157.5 total for non-directional
                # can't rename individually?
                length = len(raw.annotations)

                # try just separating based off alternating indexes
                dir_annot = raw.annotations.copy()[range(0, len(raw.annotations), 2)]
                indir_annot = raw.annotations.copy()[range(1, len(raw.annotations), 2)]

                dir_annot.rename({'1.0': 'Directional'})
                indir_annot.rename({'1.0': 'Indirectional'})

                # recombine and fix into raw obj
                raw.set_annotations(
                    dir_annot.__add__(indir_annot))

                raw.annotations.set_durations(durations, verbose=True)

                events, event_dict = mne.events_from_annotations(
                    raw,
                    verbose=False)

                subject = raw.info['subject_info']['his_id'][:participant_num_len]

            except:
                print("Something when wrong when processing the task " +\
                    "info into the MNE raw object.")
                print("Skipping:", ses)
                continue

    ### PREPROCESSING ###
    #####################
    try:
        pp = raw.copy()

        # convert to optical density
        raw_od = mne.preprocessing.nirs.optical_density(pp)

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

        pp = haemo_bp.copy()

    except:
        print("Something went wrong during preprocessing.")
        print("Skipping:", ses)
        continue

    ### SAVE DATA ###
    #################
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

    """
    # try to save the file as .fif
    try:
        pp.save(
            outpath,
            overwrite=force)
    except:
        print("Couldn't save data as '.fif'")
        print("Skipping '.fif' save for:", ses)

    # try to export the raw object for EEGLAB
    try:
        pp.export(
            outpath.replace('.fif', '.set'),
            add_ch_type=True,
            fmt='auto',
            overwrite=force)
    except:
        print("Couldn't save data as '.set'")
        print("Skipping '.fif' save for:", ses)

    # try to save file as a dataframe / csv
    try:
        df = pp.to_data_frame(index='time')
        df.to_csv(outpath.replace('.fif', '.csv'))
    except:
        print("Couldn't save data as '.csv'")
        print("Skipping '.csv' save for:", ses)

    # save annotations as dataframe / csv as well
    try:
        df = pp.annotations.to_data_frame()
        df.to_csv(outpath.replace('.fif', '_annotations.csv'))
    except:
        print("Couldn't save annotations as '.csv'")
        print("Skipping annotation save for:", ses)
    """

    ### Make mne.io.Raw into mne.Epochs ###
    #######################################

    try:
        events, event_dict = mne.events_from_annotations(pp)
        reject_criteria = dict(hbo=200e-6)

        #print(events)
        #print(event_dict.keys())
        #print(event_dict.values())

        #print("sfreq:", pp.info['sfreq'])

        if task == 'Flanker':

            tmin, tmax = -5, 63

            for j, evt in enumerate(event_dict.keys()):
                times = [t[0]/pp.info['sfreq'] for t in events if t[2] == event_dict[evt]]

                for k, time in enumerate(times):
                    crop = pp.copy().crop(
                        tmin=time+tmin,
                        tmax=time+(tmax / (j+1)))

                    crop = crop.copy().pick([
                        'S3_D2 hbo',
                        'S4_D2 hbo',
                        'S5_D3 hbo',
                        'S6_D3 hbo'])

                    df = crop.to_data_frame(index='time')
                    df['mean'] = df.mean(axis=1)
                    df.to_csv(outpath.replace('.fif', '_epoch_{}_{}.csv'.format(
                        evt, k)))
    except:
        print("Something went wrong during epoching.")
        print("Skipping session:", ses)
