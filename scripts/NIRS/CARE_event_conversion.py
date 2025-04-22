import sys, os, shutil
from os.path import join
from glob import glob
from tqdm import tqdm
import pandas as pd
import numpy as np

sys.path.append('/storage1/fs1/perlmansusan/Active/moochie/github/')
from LCBDtools.src import argParser

# parameters
#nirs_dir = "/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/NIRS_data_clean_2/"
#psypy_dir = "/storage1/fs1/perlmansusan/Active/moochie/study_data/CARE/task_data/DB_DOS/"

nirs_dir = "/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/NIRS_data_clean_2/"
psypy_dir = "/storage1/fs1/perlmansusan/Active/moochie/study_data/CARE/task_data/DB_DOS/"

ex_subs = []
participant_num_len = 5
sample_rate = 7.81250
n_blocks = 3


nirs_session_dirs = [os.path.split(d)[0] for d in glob(
    nirs_dir+"**/*_probeInfo.mat",
    recursive=True) \
    if d.strip(nirs_dir).strip("/")[:participant_num_len] not in ex_subs and \
        "V" in (os.path.basename(os.path.dirname(os.path.dirname(d))))]


print(f"The script found {len(nirs_session_dirs)} subjects available to be converted...")

def timeconvert_psychopy_to_nirstar(
    sample_rate,
    NSstim1_t,
    PSstim1_t,
    PSevent_t):
    
    NSevent_t = NSstim1_t + (PSevent_t - PSstim1_t) * sample_rate
    return NSevent_t

for ses in tqdm(nirs_session_dirs):
    # should always work, even with multiple-runs. 
    # TODO remember that these exist, where 2 runs are collected
    # for the same dyad of parent/child, for unknown reason. 
    # potentially check for truncated run while parsing this data in other
    # mne processing software
    
#     if ("50170_V0_fNIRS" in ses) or ("50171_V0_fNIRS" in ses):
#         pass
#     else:
#         continue
    
    # only do this if there's only 1 .evt file in study folder
    og_evt = glob(ses+"/*.evt")
    if len(og_evt) != 1:
        print("Error: found", len(og_evt), "evt files for the given sub / visit.")
        print("Skipping:", ses)
        continue
    else:
        og_evt = og_evt[0]
    
    # open original evt
    print(og_evt)
    f = open(og_evt, 'r')
    line1 = f.readline()
    print(line1)
    f.close()
    
    # first time marker is NIRS stim start 1
    NSstim1_t = line1.split('\t')[0]
    
    if NSstim1_t == '':
        print('Empty event file, skipping...')
        continue
    
#     print(ses)
    child_sub = ses.strip(nirs_dir).strip("/")[:participant_num_len]
#     print(child_sub)
    visit_ID = ses.strip(nirs_dir).strip("/")[participant_num_len+1:participant_num_len+3]
#     print(visit_ID)
    # looks like it's working!
    
    print(f"Looking for {psypy_dir, child_sub, visit_ID}")
    
    task_file = glob(join(psypy_dir, child_sub, visit_ID)+ "/*.csv")
    
    print(f"Task Files: {task_file}")
    
    # only continue if we have exactly 1 task file found
    if len(task_file) != 1:
        print("Error: found", len(task_file), "task files for the given sub / visit.")
        continue
    else:
        task_file = task_file[0]
      
    # df of psychopy csv output
    df = pd.read_csv(task_file)
    
    stims = []
    
    # iterate through any column that has "countdown" and ".started"
    block_i = 0
    for col in df.columns:
        
        # if we're dealing with a legitimate block column
        if ("intro_txt" in col) and (".stopped" in col):

            # then also generate the name of the corresponding stop column
            block_name_str = col.strip("intro_txt").strip(".stopped")
            
            stopcol = "timeup_txt"+block_name_str+".started"
            
            # store any non-NaN vals in the start and stop column (times)
            starts = (df[~df[col].isnull()][col].astype(float) + 5).tolist()
            stops = (df[~df[stopcol].isnull()][stopcol].astype(float)).tolist()
            
            if len(starts) != len(stops):
                print("Unequal number of starts and stops. ses:", ses, "block_i", block_i)
                continue
            
            # if there are no starts already entered / outlines has length 1,
            # then we know that the first start in our starts is the same as line1 trigger. 
            # meaning that is the reference point to which the time course of the psychopy
            # file and the NIRS file will be aligned, again using the sample rate
            # or, easily, if block_i == 1.
            
            # append to stims with tuples of (time, evt_stim_col)
            for i in range(len(starts)):
                stims.append((starts[i], block_i))
                stims.append((stops[i], 7))
            
            # if we're in the first block, we know psychopy stim 1 now
            if block_i == 0:
                PSstim1_t = starts[0]
                stims.pop(0)
            
            # convert using first NIRS stim and first Psychopy stim to align
            converted_stims = []
            
            for (time, val) in stims:
                converted_stims.append((
                    timeconvert_psychopy_to_nirstar(
                        float(sample_rate),
                        float(NSstim1_t),
                        float(PSstim1_t),
                        float(time)),
                    val))
            
            block_i += 1
        
        # if we're not dealing with a legitimate column, we can just keep iterating
        else:
            continue

    output_lines = [line1]
    
    for (stim_time, stim_col) in converted_stims:
        # make bit format stims
        evts = [0]*8
        evts[stim_col]=1
        
        # and write these as lines in correct format for .evt
        line = str(round(stim_time))
        for evt_col in evts:
            line += "\t"
            line += str(evt_col)
        line += "\n"
            
        output_lines.append(line)
    
    # move OG evt to _old.evt
    shutil.move(
        og_evt,
        og_evt.replace(".evt", "_old.evt"))
    
    # write the lines as the new, properly named .evt
    f = open(join(ses, og_evt), 'w')
    
    for line in output_lines:
        f.write(line)
    
    f.close()