"""

Builds a list of valid participants to use in FMRIPREP, and writes out to participants.txt

i.e. those subjects in the given BIDS directory which contain generally usable 
- T1w
- a functional run

usage: python3 participant_list_builder.py <path/to/bids/dataset>  
"""

import sys
import os, shutil
from os.path import join
from glob import glob

bids_folder = sys.argv[1] 

f = open(join(os.path.dirname(os.path.dirname(bids_folder)), "participant_list.txt"), 'w')

# sub_folders = [join(bids_folder, folder) for folder in os.listdir(bids_folder)]

sub_folders = glob(bids_folder+"/sub-*/**/func/*.nii.gz", recursive=True)

subs = list(set([os.path.basename(sub).split('_')[0].strip('sub-') for sub in sub_folders]))

for sub in subs:
    conf = glob(
        join(bids_folder, "derivatives", "fmriprep", "sub-"+sub)+"**/*confounds*.tsv",
        recursive=True)
    if len(conf) < 1:
        f.write(sub)
        f.write('\n')

f.close()

# for sub in sub_folders:
#    if os.path.isdir(join(sub, "anat")):
#        if os.path.isdir(join(sub, "func")):
#            if len
