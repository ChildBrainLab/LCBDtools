"""

Builds a list of valid participants to use in FSL, and writes out to fsl_subs.txt

i.e. those subjects in the fmriprep folder of the given BIDS directory which contain generally usable 
- T1w
- a functional run

usage: python3 participant_list_builder.py <path/to/bids/dataset> <FD threshold>
"""

import sys
import os, shutil
from os.path import join
from glob import glob
import pandas as pd
import numpy as np

def check_FD(ses, fd_thresh, perc=0.15):
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
    fd = np.array(df["framewise_displacement"].astype(float))
    za = (fd > fd_thresh).sum()
    if (za / len(fd)) > perc:
        return False
    else:
        return True

bids_folder = sys.argv[1] 

if len(sys.argv) > 2:
    fd_thresh = float(sys.argv[2])

f = open("/home/"+str(os.environ.get("USER"))+"/fsl_subs.txt", 'w')

# sub_folders = [join(bids_folder, folder) for folder in os.listdir(bids_folder)]
ses_folders = [ses.replace(bids_folder, "") for ses in glob(bids_folder+"/sub*/ses*") if \
    len(glob(ses+"/func/*.nii.gz")) > 0]

#print("ses folders:", ses_folders)

fp_ses_folders = [ses for ses in glob(bids_folder+"/derivatives/fmriprep/sub*/ses*/func/")]

fp_ses_folders = [ses for ses in fp_ses_folders if len(glob(ses+"/*movieB*preproc_bold.nii.gz")) > 0]

fp_ses_folders = [ses.replace(bids_folder+"/derivatives/fmriprep/", "") for ses in fp_ses_folders]

#print("fp ses folders:", fp_ses_folders)

#unfp_ses = [ses for ses in ses_folders if ses not in fp_ses_folders]

#unfp_subs = [ses.split('/')[0] for ses in unfp_ses]

#print(unfp_subs)

valid_ses_folders = []

for ses in fp_ses_folders:
    if len(sys.argv) > 2:
        if check_FD(ses, fd_thresh):
            valid_ses_folders.append(ses)
    else:
        valid_ses_folders.append(ses)

for ses in valid_ses_folders:
    f.write(ses)
    f.write('\n')
