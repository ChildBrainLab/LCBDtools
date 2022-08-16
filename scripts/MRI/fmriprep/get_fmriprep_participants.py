"""

Builds a list of valid participants to use in FMRIPREP, and writes out to participants.txt

i.e. those subjects in the given BIDS directory which contain generally usable 
- T1w
- a functional run

usage: python3 get_fmriprep_participants.py <path/to/bids/dataset>  
"""

import sys
import os, shutil
from os.path import join
from glob import glob

bids_folder = sys.argv[1] 

f = open("/home/"+str(os.environ.get("USER"))+"/participant_list.txt", 'w')

ses_folders = [ses.replace(bids_folder, "") for ses in glob(bids_folder+"/sub*/ses*") if \
    len(glob(ses+"/func/*.nii.gz")) > 0]

fp_ses_folders = [ses.replace(bids_folder+"/derivatives/fmriprep/", "") for ses in glob(bids_folder+"/derivatives/fmriprep/sub*/ses*")]

unfp_ses = [ses for ses in ses_folders if ses not in fp_ses_folders]

unfp_subs = [ses.split('/')[0] for ses in unfp_ses]

for sub in list(set(unfp_subs)):
    f.write(sub)
    f.write('\n')
