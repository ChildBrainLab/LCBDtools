"""

Writes .txt files for use in either FSL or MATLAB of relevant columns from
confounds.tsv files output during FMRIPREP

usage: python3 extract_confounds.py <path/to/bids/dataset>
"""

import sys
import os, re, shutil
from os.path import join
from glob import glob
import pandas as pd
import numpy as np

bids_folder = sys.argv[1]

COIs = [
    "framewise_displacement",
    "trans_x",
    "trans_y",
    "trans_z",
    "rot_x",
    "rot_y",
    "rot_z",
]

cons = glob(bids_folder+"/derivatives/fmriprep/sub-*/**/func/*confounds_timeseries.tsv")

for fname in cons:
    df = pd.read_csv(fname, delimiter="\t", usecols=COIs)
    for col in COIs:
        series = df[col].astype(float)
        if col == "framewise_displacement":
            series[0] = float(0.0)

        new_fname = fname.replace("timeseries", col).replace("tsv", "txt")

        # if not os.path.exists(new_fname):

        f = open(new_fname, 'w')

        for i, val in enumerate(series):
            if i > 0:
                f.write('\n')
            f.write(str(val))

        f.close()
