"""

Builds a list of valid participants to use in FSL, and writes out to fsl_subs.txt

i.e. those subjects in the fmriprep folder of the given BIDS directory which contain generally usable 
- T1w
- a functional run

usage: python3 get_fsl_subs.py <path/to/bids/dataset> optional: <task> <FD_thresh> <FD_perc> <run_length>
"""

import sys
import os, shutil
from os.path import join
from glob import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
sys.path.append('../..')
import argParser


args = argParser.main([
    "data_folder",
    "task",
    "FD_thresh",
    "FD_perc",
    "run_length"
    ])

def check_FD(ses, fd_thresh, perc=0.30):
    """
    Checks confounds .tsv file for framewise displacement exclusions

    :param ses: path to functional folder for given sub/ses
    :type ses: str
    :param fd_thresh: the threshold (in mm) over which outlier values are selected
    :type fd_thresh: float
    :param perc: max. percentage of FD values for which threshold can be exceeded
    :type perc: float

    :returns: False if excessive motion, True if pass check
    """
    conf = glob(
        join(bids_folder, "derivatives", "fmriprep", ses, "**/*confounds*.tsv"),
        recursive=True)[0]

    df = pd.read_csv(conf, delimiter="\t", usecols=["framewise_displacement"])
    # skim 1 because first FD always N/A
    fd = np.array(df["framewise_displacement"].astype(float))[1:]
    za = (fd > fd_thresh).sum()
    # add the 1 back into the length for perfect %
    if (za / (len(fd)+1)) > perc:
        return False
    else:
        return True

def get_FD_len(ses):
    """
    Checks confounds .tsv file to return number of volumes

    Probably used with the mode of the length of confounds file, or more specifically
    used with the check_FD function and therefore the length of FD-1 (first N/A is removed)

    :param ses: path to functional folder for given sub/ses
    :type ses: str
    :param num: the number of volumes that should be present
    :type num: int

    :returns: False if a different number than the number is included, else True
    """
    conf = glob(
        join(bids_folder, "derivatives", "fmriprep", ses, "**/*confounds*.tsv"),
        recursive=True)[0]

    df = pd.read_csv(conf, delimiter="\t", usecols=["framewise_displacement"])
    fd = np.array(df["framewise_displacement"].astype(float))
    
    return len(fd)

# load argparse arguments
bids_folder = args.data_folder
fd_thresh = float(args.fd_thresh)
min_length = float(args.run_length)
task = str(args.task)

# open ~/fsl_subs.txt for writing
f = open("/home/"+str(os.environ.get("USER"))+"/fsl_subs.txt", 'w')

# fmriprepped session folders (independent of whether ses folders are present or not)
fp_ses_folders = [ses for ses in glob(bids_folder+"/derivatives/fmriprep/**/func/", recursive=True)]
total_fp_folds = len(fp_ses_folders)

# select for only fprep sessions where a valid fprep gz output is present
fp_ses_folders = [ses for ses in fp_ses_folders if \
    len(glob(ses+"/*{}*preproc_bold.nii.gz".format(task))) > 0]
valid_fp_folds = len(fp_ses_folders)

# remove pre-fmriprep part of path
fp_ses_folders = [ses.replace(bids_folder+"/derivatives/fmriprep/", "") for ses in fp_ses_folders]

valid_ses_folders = []
length_of_FDs = []

for ses in tqdm(fp_ses_folders):
    if check_FD(ses, fd_thresh, perc=float(args.fd_perc)):
        valid_ses_folders.append(ses)
        length_of_FDs.append(get_FD_len(ses))

sessions = []
lmax = np.max(length_of_FDs)

for (ses, length) in zip(valid_ses_folders, length_of_FDs):
    if length >= lmax*min_length:
        sessions.append(ses)

for ses in sessions:
    smoothgz = glob(bids_folder+"/derivatives/fmriprep/"+ses+"/*smoothed*.gz")[0]
    smoothgz = smoothgz.replace(bids_folder+"/derivatives/fmriprep/", "")
    f.write(smoothgz)
    f.write('\n')

f.close()

print("{} subjects were retained from {} total valid scans".format(len(sessions), valid_fp_folds))
