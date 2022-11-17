"""

Builds a list of valid participants to use in FMRIPREP, and writes out to participants.txt

i.e. those subjects in the given BIDS directory which contain generally usable 
- T1w
- a functional run

usage: python3 get_fmriprep_participants.py --data_folder </path/to/BIDS/dir> --visit ses-0 --force True
"""

import sys
import os, shutil
from os.path import join
from glob import glob

sys.path.append('../..')
import argParser

args = argParser.main([
    "data_folder",
    "visit",
    "force"
    ])

bids_folder = args.data_folder
if bids_folder[-1] != "/":
    bids_folder = bids_folder + "/"

session = args.visit
if session in [0, 1, 2]:
    session = "ses-"+str(session)
if session not in ['ses-0', 'ses-1', 'ses-2']:
    print("Valid session number not provided. Must be one of: {0, 1, 2}. Setting to None (i.e. not filtering for session.")
    session = None

force = args.force

# open the participant list file
f = open("/home/"+str(os.environ.get("USER"))+"/participant_list.txt", 'w')

# all BIDS sub/ses that contain NIGZ functional data
ses_folders = ['/'.join(ses.replace(bids_folder, "").split('/')[:2]) for ses in glob(os.path.join(bids_folder, "sub*", "ses*", "func", "*bold.nii.gz"))]

# if the confounds.tsv file is present in the fmriprep folder, then it is completed
# so we get all sub/ses that have completed FMRIPREP data
fp_ses_folders = list(set([
    '/'.join(ses.replace(bids_folder+"/derivatives/fmriprep/", "").split('/')[:2]) for ses in \
        glob(bids_folder+"/derivatives/fmriprep/sub*/**/*confounds*.tsv", recursive=True)
]))

# if we are using force, then we should ignore that some subjects are already complete
if force is True:
    unfp_ses = ses_folders
# otherwise, we prune the subjects who are already complete
else:
    unfp_ses = [ses for ses in ses_folders if ses not in fp_ses_folders]

#print("fp ses folders:", fp_ses_folders)
#print("all BIDS func data:", ses_folders)
#print("unfp sess:", unfp_ses)

# then also prune just for the sessions we care about
if session is not None:
    unfp_ses = [ses for ses in unfp_ses if session in ses]

# and take just the subject numbers from that sub/ses list
unfp_subs = [ses.split('/')[0] for ses in unfp_ses]

unfp_subs = sorted(list(set(unfp_subs)))

print(unfp_subs)

for sub in unfp_subs:
    f.write(sub)
    f.write('\n')

print("Saved to: ~/participant_list.txt")
