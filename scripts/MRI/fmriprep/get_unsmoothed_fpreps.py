"""
usage: python3 get_unsmoothed_fpreps.py <path/to/bids/dataset>  
"""

import sys
import os, shutil
from os.path import join
from glob import glob

bids_folder = sys.argv[1] 

f = open("/home/"+str(os.environ.get("USER"))+"/smooth_subs.txt", 'w')

preprocs = glob(bids_folder+"/derivatives/fmriprep/sub-*/ses-*/func/*preproc_bold.nii.gz")

unsmoothed_niis = []

for nii in preprocs:
    if len(glob(os.path.split(nii)[0]+"/*smoothed*")) == 0:
        unsmoothed_niis.append(nii)

for nii in unsmoothed_niis:
    f.write(nii)
    f.write('\n')

f.close()
