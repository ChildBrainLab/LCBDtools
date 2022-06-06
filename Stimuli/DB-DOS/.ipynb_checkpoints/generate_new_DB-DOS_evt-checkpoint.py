# usage: python3 generate_new_DB-DOS_evt.py

import sys
import os, shutil
from os.path import join
from glob import glob
from tqdm import tqdm
import pandas as pd

sys.path.append('../../..')
from preprocessing.scripts import argParser

args = argParser.main([
    "data_folder",
    "task_folder",
    "ex_subs",
    "participant_num_len",
    "in_subs",
    "sample_rate"
])

nirs_dir = args.data_folder
psypy_dir = args.task_folder
ex_subs = args.ex_subs
participant_num_len = args.participant_num_len
in_subs = args.in_subs
sample_rate = args.sample_rate

def timeconvert_psychopy_to_nirstar(
    sample_rate,
    NSstim1_t,
    PSstim1_t,
    PSevent_t):
    
    NSevent_t = NSstim1_t + (PSevent_t - PSstim1_t) * sample_rate
    return NSevent_t

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

if len(session_dirs) == 0:
    print("No session directories were considered valid.")
    sys.exit(3)
    
for ses in tqdm(session_dirs):
    
    child_sub = ses.strip(nirs_dir).strip("/")[:participant_num_len]
    visit_ID = ses.strip(nirs_dir).strip("/")[participant_num_len+1:participant_num_len+3]
    
    # check for any .csv matching session ID and make sure just 1 exists
    task_file = glob(join(psypy_dir, child_sub, visit_ID)+ "/*.csv")
    if len(task_file) != 1:
        print("Error: found", len(task_file), "task files for the given sub / visit:", ses)
        continue
    else:
        task_file = task_file[0]
        
    # df of psychopy csv output
    df = pd.read_csv(task_file)
    
    # make sure only one .evt for the given sub (because we are renaming / overwriting)
    og_evt = glob(ses+"/*.evt")
    if len(og_evt) != 1:
        print("Error: found", len(og_evt), "evt files for the given sub / visit.")
        print("Skipping:", ses)
        continue
    else:
        og_evt = og_evt[0]
    
    # read first line of original .evt file, because this stimuli happens
    # to be correct. thankfully it is, at least in most cases... 
    try:
        f = open(og_evt, 'r')
        first_stim_check = False
        i = 0
        # until we have a stim that actually makes sense
        while first_stim_check is False:
            
            line1 = f.readline()
            i += 1
            NSstim1_t = line1.split('\t')[0]
            stimcols = line1.split('\t')[1:]
            onstimcols = [col for col in range(len(stimcols)) \
                if stimcols[col] == '1']
            if len(onstimcols) == 0:
                print("No stimuli were on during first stim of NIRStar OG .evt file?")
                raise ValueError
            else:
                for col in onstimcols:
                    if col < 4:
                        first_stim_check = True
        f.close()
        
        line1new = line1.split('\t')[0]
        line1new += "\t"
        line1new += "1"
        line1new += ("\t"+"0")*7
        line1new += "\n"
        
        # start output_lines, list of all lines which we'll write
        # to the new .evt
        output_lines = [line1new]
    except:
        f.close()
        print("Something went wrong trying to determind the first stimulus of the \
             original stimulus file, skipping session:", ses)
        print("The program reached line", i, "of the original .evt file, \
            without finding an apparently valid stimulus, before exiting.")
        continue
    
    try:
        # iterate through any column that has "countdown" and ".started"
        block_i = 0
        # and we're going to store info about each stim here
        stims = []
        for col in df.columns:

            # if we're dealing with a legitimate block column
            if ("intro_txt" in col) and (".stopped" in col):

                # then also generate the name of the corresponding stop column
                block_name_str = col.strip("intro_txt").strip(".stopped")
                stopcol = "timeup_txt"+block_name_str+".started"

                # store any non-NaN vals in the start and stop column (times)
                # i.e. only the rows of the PsychoPy output datasheet
                # that are relevant for this particular block / column.
                starts = (df[~df[col].isnull()][col].astype(float) + 5).tolist()
                stops = (df[~df[stopcol].isnull()][stopcol].astype(float)).tolist()

                # check to make sure there's a stop row for every start row
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

                # if we're on the first block, we can pop
                if block_i == 0:
                    PSstim1_t = starts[0]
                    stims.pop(0)

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
    except:
        print("For some reason the PsychoPy dataframe could not be parsed correctly.")
        print("Skipping session:", ses)
        continue
    
    for (stim_time, stim_col) in converted_stims:
        evts = [0]*8
        evts[stim_col]=1
        
        line = str(round(stim_time))
        for evt_col in evts:
            line += "\t"
            line += str(evt_col)
        line += "\n"
            
        output_lines.append(line)
    
    try:
        shutil.move(
            og_evt,
            og_evt.replace(".evt", "_old.evt"))
    except:
        print("The original .evt wasn't moved, so the session was abandoned.")
        print("Session is left as is:", ses)
        continue
        
    try:
        f = open(join(ses, og_evt), 'w')
        for line in output_lines:
            f.write(line)
            
        f.close()
    except:
        print("The new .evt file couldn't be written, but the original was moved.")
        print("Session:", ses, "needs attention.")
        continue
    
    
    
    
    
    
    