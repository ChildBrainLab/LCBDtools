"""
usage: python3 get_unsusand_fpreps.py <path/to/bids/dataset>  
"""

import sys
import os, shutil
from os.path import join
from glob import glob

bids_folder = sys.argv[1] 

f = open("/home/"+str(os.environ.get("USER"))+"/susan_subs.txt", 'w')

preprocs = glob(bids_folder+"/derivatives/fmriprep/sub-*/**/*preproc_bold.nii.gz", recursive=True)

unsmoothed_niis = []

for nii in preprocs:
    susanstr = nii.replace(".nii.gz", "_susan.nii.gz")
    if len(glob(susanstr)) == 0:
        unsmoothed_niis.append(nii)

for nii in unsmoothed_niis:
    f.write(nii)
    f.write('\n')

f.close()
