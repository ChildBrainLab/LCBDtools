"""
usage: python3 get_uninversed_bet_masks.py <path/to/bids/dataset>  
"""

import sys
import os, shutil
from os.path import join
from glob import glob

bids_folder = sys.argv[1] 

f = open("/home/"+str(os.environ.get("USER"))+"/inversemask_subs.txt", 'w')

preprocs = glob(bids_folder+"/derivatives/fmriprep/**/func/*brain_mask*.nii.gz", recursive=True)
preprocs = [p for p in preprocs if "inverse" not in p]

uninversed_niis = []

for nii in preprocs:
    uninv=nii.replace("brain_mask", "brain_mask_inverse")
    if len(glob(uninv)) == 0:
        uninversed_niis.append(nii)

for nii in uninversed_niis:
    f.write(nii)
    f.write('\n')

f.close()
