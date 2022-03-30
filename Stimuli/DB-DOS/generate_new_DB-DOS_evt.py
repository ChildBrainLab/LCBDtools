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
    "participant_num_len"
])

nirs_dir = args.data_folder
psypy_dir = args.task_folder
ex_subs = args.ex_subs
participant_num_len = args.participant_num_len

session_dirs = [os.path.split(d)[0] for d in glob(
    nirs_dir+"**/*_probeInfo.mat",
    recursive=True) \
    if d.strip(nirs_dir).strip("/")[:participant_num_len] not in ex_subs]
