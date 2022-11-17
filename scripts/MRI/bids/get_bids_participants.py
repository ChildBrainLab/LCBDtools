import os, shutil
from glob import glob
import sys
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
f = open("/home/"+str(os.environ.get("USER"))+"/bids_list.txt", 'w')

source_sessions = [session.replace(bids_folder+"/sourcedata", "") for session in \
    glob(bids_folder+"/sourcedata/*/*")]

bids_sessions = [session.replace(bids_folder, "") for session in \
    glob(bids_folder+"sub-*/ses-*")]


unbids_convd = [] 

for session in source_sessions:

    bidsvers = "sub-"+os.path.split(session)[0].strip("/")+"/ses-"+os.path.split(session)[1]

    if bidsvers not in bids_sessions:

        unbids_convd.append(os.path.split(bidsvers)[0])

unbids_convd = sorted(unbids_convd)
print(unbids_convd)

for sub in unbids_convd:
    f.write(sub.replace("sub-", ""))
    f.write('\n')

f.close()

print("Saved to: ~/bids_list.txt")


    
