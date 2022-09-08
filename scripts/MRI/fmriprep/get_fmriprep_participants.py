"""

Builds a list of valid participants to use in FMRIPREP, and writes out to participants.txt

i.e. those subjects in the given BIDS directory which contain generally usable 
- T1w
- a functional run

usage: python3 get_fmriprep_participants.py <path/to/bids/dataset> optional: <session> 
"""

import sys
import os, shutil
from os.path import join
from glob import glob

bids_folder = sys.argv[1] 
if len(sys.argv) > 2:
    session = sys.argv[2]
else:
    session = None

f = open("/home/"+str(os.environ.get("USER"))+"/participant_list.txt", 'w')

ses_folders = [ses.replace(bids_folder, "") for ses in glob(bids_folder+"/sub*/ses*") if \
    len(glob(ses+"/func/*.nii.gz")) > 0]

fp_ses_folders = list(set([
    '/'.join(ses.replace(bids_folder+"/derivatives/fmriprep/", "").split('/')[:2]) for ses in \
        glob(bids_folder+"/derivatives/fmriprep/sub*/**/*confounds*.tsv", recursive=True)
]))

#print(fp_ses_folders)
#exit

#fp_ses_folders = [ses.replace(bids_folder+"/derivatives/fmriprep/", "") for ses in glob(bids_folder+"/derivatives/fmriprep/sub*/ses*")]
#fp_ses_folders = [ses for ses in fp_ses_folders if os.path.exists(os.path.join(os.path.dirname(ses), "figures"))]

unfp_ses = [ses for ses in ses_folders if ses not in fp_ses_folders]

if session is not None:
    unfp_ses = [ses for ses in unfp_ses if session in ses]

unfp_subs = [ses.split('/')[0] for ses in unfp_ses]

for sub in list(set(unfp_subs)):
    f.write(sub)
    f.write('\n')
