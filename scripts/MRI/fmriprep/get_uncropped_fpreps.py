"""
usage: python3 get_uncropped_fpreps.py <path/to/bids/dataset>  
"""

import sys
import os, shutil
from os.path import join
from glob import glob

bids_folder = sys.argv[1] 

f = open("/home/"+str(os.environ.get("USER"))+"/crop_subs.txt", 'w')

preprocs = glob(bids_folder+"/derivatives/fmriprep/sub-*/**/*preproc_bold*smoothed*.nii", recursive=True)
preprocs = [p for p in preprocs if "crop" not in p]

uncropped_niis = []

for nii in preprocs:
    if len(glob(os.path.split(nii)[0]+"/*smoothed*crop*")) == 0:
        uncropped_niis.append(nii)

for nii in uncropped_niis:
    f.write(nii)
    f.write('\n')

f.close()
