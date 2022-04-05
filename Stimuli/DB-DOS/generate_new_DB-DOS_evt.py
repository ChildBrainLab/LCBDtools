# usage: python3 generate_new_DB-DOS_evt.py

import sys
import os, shutil
from os.path import join
from glob import glob
from tqdm import tqdm

sys.path.append('../../..')
from preprocessing.scripts import argParser

args = argParser.main([
    "data_folder",
    "task_folder",
    "ex_subs",
    "participant_num_len",
    "in_subs"
])

nirs_dir = args.data_folder
psypy_dir = args.task_folder
ex_subs = args.ex_subs
participant_num_len = args.participant_num_len
in_subs = args.in_subs

# all sessions that meet naming conventions
session_dirs = [os.path.split(d)[0] for d in glob(
    nirs_dir+"**/*_probeInfo.mat",
    recursive=True) \
    if d.strip(nirs_dir).strip("/")[:participant_num_len] not in ex_subs]

# generate list of subjects
subjects = list(set([os.path.basename(d)[:participant_num_len] for \
    d in session_dirs]))

# only include subs in 'in_subs', if given
if in_subs is None:
    in_subs = subjects
else:
    session_dirs = [ses for ses in session_dirs \
        if ses.strip(nirs_dir).strip("/")[:participant_num_len] in in_subs]

for ses in tqdm(nirs_session_dirs):
    