import os, sys, datetime, csv, shutil, glob
from glob import glob
from datetime import datetime
import pandas as pd

class pcat:
    # This class is used to condense p-cat flanker behavioral data and
    # annotate fnris data with relavent data in subjects NIRS .evt files.
    # Within these .evt files the columns correspond to the following order...
    # fnris sample, block, directionality, congruency, direction, response
    #
    # Correct response can be infered
    def __init__(self):
        self.beh_folder = '../../../../study_data/P-CAT/R56/restructured_data/task_data/flanker/'
        self.nirs_folder = '../../../../analysis/P-CAT/flanker_nirs/'
        self.analysis_folder = '../../../../analysis/P-CAT/'

        self.ex_subs = []
        self.participant_num_len = 4
        self.sample_rate = 7.81250

        self.master = {}
        self.translator = { # Translator used to convert stimuli info to integers for NIRS .evts files
            'ND' : '0', # 
            'D' : '1', 
            'I' : '0', # Congruency - .evt file column 
            'C' : '1',
            'L' : '0', # Directionality
            'R' : '1',
            'None': '0', # User response
            'left': '0',
            'right': '1',
            'incorrect': '0', # Accuracy
            'correct': '1'
        }

        # Functional variables
        self.pad = lambda x, n: '0'*(n - len(str(x))) + str(x) # Function for padding zeros onto subject ID

    def iterate_behavioral(self):
        task_files = glob(f'{self.beh_folder}*/*.csv')
        current_block = None
        for task_filepath in task_files: # For each task and it's given nickname find subjects data
            
            subject = task_filepath.split(self.beh_folder)[1][:4]
            subject_files =  glob(f'{self.beh_folder}{subject}/*.csv')
            
            if len(subject_files) > 1: # Make sure the file we have is the last file for the subject
                last_date = [0, 0]
                last_file = None
                for subject_file in subject_files:
                    date = [int(datum) for datum in subject_file[:-4].split('_')[-2:]]
                    if date[0] > last_date[0]:
                        last_file = subject_file
                        last_date = date
                    if date[1] > last_date[1]:
                        last_file = subject_file
                        last_date = date
                task_filepath = last_file

            print(f'Processing subject {subject}...')
            with open(task_filepath, 'r') as file: # Open file and grab data
                csvreader = csv.reader(file)
                data = [line for line in csvreader]
            
            if subject not in self.master.keys():
                self.master[subject] = {}
            for row_ind, row in enumerate(data[1:]): # Add in all data points to the list
                # Grab pertinent data
                if row[0] == None or row[0] == '': continue
                stimuli = row[0].split('/')
                if len(stimuli) == 1: 
                    print(f"Skipping {subject} row {row_ind}")
                    continue
                else:
                    stimuli = stimuli[1].split('.')[0] # Grab stimuli and remove excess
                stimuli = stimuli.split('_')

                if stimuli[0] == 'practice': continue
                
                block = stimuli[1].split('block')[1]
                if block != current_block:
                    current_block = block
                    block = 1
                else:
                    block = 0
                
                
                directionality = stimuli[2]
                if directionality == 'D':
                    direction = stimuli[3][1]
                    congruency = stimuli[3][0]
                else:
                    direction = stimuli[3][0]
                    congruency = 'ND'

                response = None # Find subject response and start for trial
                start = None 
                for header_ind, header in enumerate(data[0]): # Iterate through data sheet columns and find columns of interest
                    if 'key_resp' == header[:8]:
                        if 'keys' == header[-4:]: # If the column header is in our columns of interest  
                            if row[header_ind]: # If there is an entry
                                response = row[header_ind]
                        if 'started' == header[-7:]:
                            if row[header_ind]: # If there is an entry
                                start = float(row[header_ind])

                if self.translator[response] == self.translator[direction]: accuracy = 'correct'
                else: accuracy = 'incorrect'
                
                # Translate info into .evt style numbers
                trial_data = [str(self.translator[datum]) if datum in self.translator.keys() else datum for datum in [block, directionality, congruency, direction, response, accuracy]]

                # Add info into mastersheet
                self.master[subject][str(start)] = trial_data

    def sync_nirs(self, replace = False):

        for subject in self.master.keys(): # Iterate through subjects in extract file
            print(f'Syncing {subject} NIRS data')
            # Grab task specific task filenames
            nirs_session_dir = glob(self.nirs_folder+f"{subject}/")

            if len(nirs_session_dir) < 1:
                print(f'Flanker NIRS files not found: {nirs_session_dir}')
                continue
            else:
                nirs_session_dir = nirs_session_dir[0]

            # only do this if there's only 1 .evt file in study folder
            og_evt = glob(nirs_session_dir + "*.evt")
            if len(og_evt) != 1:
                if replace == True:
                    for evt in og_evt:
                        if '_old' not in evt:
                            og_evt = evt
                else:            
                    print(f"{len(og_evt)} .evt files - Skipping: {nirs_session_dir}")
                    continue
            else:
                og_evt = og_evt[0]
            
            if subject == '1103':
                print('Found 1103!')

            # open original evt
            f = open(og_evt, 'r')
            line1 = f.readline()
            f.close()
            
            # first time marker is NIRS stim start 1
            NSstim1_t = line1.split('\t')[0]
            if NSstim1_t == None or NSstim1_t == '':
                continue
            #output_lines = [line1]
            output_lines = []

            converted_stims = []
            timestamps = sorted(self.master[subject].keys())
            if len(timestamps) > 0:
                initial_timestamp = timestamps[0]
            else:
                continue

            for timestamp in timestamps:
                converted_stims.append(( # Add stim to current stims
                    self.timeconvert_psychopy_to_nirstar(
                        float(self.sample_rate),
                        float(NSstim1_t),
                        float(timestamp),
                        float(initial_timestamp)
                        ),
                    self.master[subject][timestamp])
                )

            for (stim_time, stimuli) in converted_stims:
                line = str(round(stim_time))
                line += '\t1'
                for evt_col in stimuli:
                    line += "\t"
                    line += str(evt_col)
                #line += '\t0'
                line += "\n"
                    
                output_lines.append(line)

            # move OG evt to _old.evt
            if os.path.exists(og_evt.replace(".evt", "_old.evt")) == False:
                shutil.move(
                    og_evt,
                    og_evt.replace(".evt", "_old.evt"))
            
            # write the lines as the new, properly named .evt
            f = open(og_evt, 'w')
            
            for line in output_lines:
                f.write(line)
            
            f.close()
        return

    def timeconvert_psychopy_to_nirstar(self, sample_rate, NSstim1_t, timestamp, initial_timestamp):
        NSevent_t = (timestamp - initial_timestamp) * sample_rate # Remove NSstim1
        return NSevent_t

    def save_master(self):
        final_master = {}
        headers = ['block', 'directionality', 'congruency', 'direction', 'response', 'accuracy']
        for subject in self.master.keys():
            for timepoint in self.master[subject].keys():
                row = f'{subject}-{timepoint}'
                if row not in final_master.keys():
                    final_master[row] = {potential_header:None for potential_header in headers}
                
                final_master[row] = self.master[subject][timepoint]
                            
        dataset = [['ID', 'Time'] + headers]
        for row in final_master.keys():
            data = final_master[row]
            dataset.append(row.split('-') + data)

        with open(f'{self.analysis_folder}P-CAT_Behavioral_Masterfile.csv', 'w') as file:
            csvwriter = csv.writer(file)
            for row in dataset:
                csvwriter.writerow(row)



class emogrow:
    def __init__(self):
        self.master_filename = '../../../../study_data/EmoGrow/emogrow_master.xlsx'
        self.beh_folder = '../../../../study_data/EmoGrow/task_behavioral_data/exported_task_data/'
        self.nirs_folder = '../../../../study_data/EmoGrow/NIRS_data/'
        self.analysis_folder = '../../../../analysis/EmoGrow/'

        self.ex_subs = []
        self.participant_num_len = 3
        self.sample_rate = 7.81250

        self.master = {}
        self.ex_subs = []

        # Define variables for scraping data
        self.tasks = ['GoNoGo', 'Monkey', 'PetStore', 'FETCH'] # Task names for referencing files
        self.task_filenames = ['GoNoGo', 'Monkey', 'PetStoreStroop', 'FETCH']
        self.nicknames = ['Go', 'Mon', 'Pet', 'Fet'] # Task nicknames for masterfile headers
        self.scan_order_name = ['Go_No_Go', 'Monkey', 'PetStoreStroop', 'Fetch']
        self.coi = {'GoNoGo': ['ShowImage.ACC', 'ShowImage.RT'], 'Monkey': ['Trialend.ACC', 'Trialend.RT'], 'PetStore': ['Slide1.ACC', 'Slide1.RT'],'FETCH': ['FetchTrialWin.RT', 'responseemoscalewin', 'responseemoscalelose', 'responseemoscalewinfinal']} # Define columns of interest (coi) to scrap from each file
        self.task_onset_headers = {'GoNoGo': 'ShowImage.OnsetTime', 'Monkey': 'Trialend.OnsetTime', 'PetStore': 'Slide1.OnsetTime', 'FETCH': 'FetchTrialWin.OnsetTime'}
        self.running_block_names = {'GoNoGo': 'GoNoGo', 'Monkey': 'List', 'PetStore': 'Stroop', 'FETCH': 'Block'}

        # Functional variables
        self.pad = lambda x, n: '0'*(n - len(str(x))) + str(x) # Function for padding zeros onto subject ID

    def iterate_behavioral(self):
        mastersheet = pd.read_excel(self.master_filename, 'Sheet1', engine='openpyxl') # Open up master file in 

        for subject in mastersheet['Name']: # Iterate through subjects in extract file
            subject = self.pad(subject, 3)
            self.master[subject] = {} #  Create an entry for participant in master dictionary
            
            for timepoint in ['V1', 'V3', 'V5']: # Call for each potential timepoint
                self.master[subject][timepoint] = {nickname:{} for nickname in self.nicknames}
                
                for (task, task_filename, nickname) in zip(self.tasks, self.task_filenames, self.nicknames): # For each task and it's given nickname find subjects data
                    filepath = f'{self.beh_folder}fNIRS_{task}/{task_filename}_{subject}_{timepoint}_1.csv' # Generate potential filepath
                    if os.path.exists(filepath) == False: continue # Move past potential data if it doesn't exist
                    else:   self.master[subject][timepoint][nickname] = {} # Create a data entry list

                    with open(filepath, 'r') as file: # Open file and grab data
                        csvreader = csv.reader(file)
                        data = [line for line in csvreader]
                    
                    for header_ind, header in enumerate(data[0]): # Iterate through data sheet columns and find columns of interest
                        if header in self.coi[task]: # If the column header is in our columns of interest
                            self.master[subject][timepoint][nickname][header] = []
                            for row in data[1:]: # Add in all data points to the list
                                self.master[subject][timepoint][nickname][header].append(row[header_ind])

    def sync_nirs(self):
        mastersheet = pd.read_excel(self.master_filename, 'Sheet1', engine='openpyxl') # Open up master file in 

        for subject in mastersheet['Name']: # Iterate through subjects in extract file

            self.master[self.pad(subject, 3)] = {} #  Create an entry for participant in master dictionary
            
            for timepoint in ['V1', 'V3', 'V5']: # Call for each potential timepoint
                self.master[self.pad(subject, 3)][timepoint] = {nickname:{} for nickname in self.nicknames}
                
                for (task, task_filename, nickname, scan_name) in zip(self.tasks, self.task_filenames, self.nicknames, self.scan_order_name): # For each task and it's given nickname find subjects data
                    onset_header = self.task_onset_headers[task]
                    block_name = self.running_block_names[task]
                    
                    blocks = {}
                    block_count = 0
                    
                    filepath = f'{self.beh_folder}fNIRS_{task}/{task_filename}_{self.pad(subject, 3)}_{timepoint}_1.csv' # Generate potential filepath
                    if os.path.exists(filepath) == False: continue # Move past potential data if it doesn't exist

                    
                    scan_number = mastersheet[mastersheet['Name'] == subject][scan_name].values[0] # Find scan number in scan order sheet

                    with open(filepath, 'r') as file: # Open file and grab data
                        csvreader = csv.reader(file)
                        data = [line for line in csvreader]

                    # Find task scan number for DBDOS
                    #sub1_scan_number = mastersheet[f'{scan_name}1']
                    #sub2_scan_number = mastersheet[f'{scan_name}2']

                    # Grab task specific task filenames
                    nirs_session_dir = glob(self.nirs_folder+f"{self.pad(subject, 3)}/{timepoint}/*/*{scan_number}/")
                    if len(nirs_session_dir) < 1:
                        print(f'Directory not found: {nirs_session_dir}')
                        continue
                    else:
                        nirs_session_dir = nirs_session_dir[0]

                    # only do this if there's only 1 .evt file in study folder
                    og_evt = glob(nirs_session_dir + "/*.evt")
                    if len(og_evt) != 1:
                        print(f"{len(og_evt)} .evt files - Skipping: {nirs_session_dir}")
                        continue
                    else:
                        og_evt = og_evt[0]
                    
                    # open original evt
                    f = open(og_evt, 'r')
                    line1 = f.readline()
                    f.close()
                    
                    # first time marker is NIRS stim start 1
                    NSstim1_t = line1.split('\t')[0]
                    if NSstim1_t == None or NSstim1_t == '':
                        continue
                    output_lines = [line1]

                    # Open the task and read in task data
                    filepath = f"{self.beh_folder}fNIRS_{task}/{task_filename}_{self.pad(subject, 3)}_{timepoint}_1.csv"
                    with open(filepath, 'r') as file: # Open file and grab data
                        csvreader = csv.reader(file)
                        data = [line for line in csvreader]
                
                    for header_ind, header in enumerate(data[0]): # Iterate through data sheet columns and find columns of interest
                        if header == onset_header: # If start timestamp found
                            onset_ind = header_ind
                        if header in self.coi[task]: # If column of interest for task
                            coi_ind = header_ind # Grab column of interest index
                        if header == 'Running': # If column of interest for block indicator
                            running_ind = header_ind

                    PSstim1_t = data[1][onset_ind]

                    converted_stims = []
                    for ind, datum in enumerate(data[1:]): # Iterate through task file
                        if datum[running_ind][:len(block_name)] != block_name: # IF the block naming scheme doesn't match our block of interest
                            continue # Skip irrelavent block
                        if datum[running_ind] not in blocks.keys(): # Update block if necessary
                            block_count += 1 # Add to block count
                            blocks[datum[running_ind]] = block_count # Assign block it's number

                        if datum[onset_ind] == None or datum[onset_ind] == '': # If onset not recorded
                            continue # Skip

                        if PSstim1_t == None or PSstim1_t == '': # If behavioral task start not found
                            PSstim1_t = datum[onset_ind] #Add onset to start
                        #else:
                        #    print(f"Converting Time --> ind {ind} | NSstim1_t: {NSstim1_t} | PSstim1_t: {PSstim1_t} | datum onset: {datum[onset_ind]}")
                       
                        

                        converted_stims.append(( # Add stim to current stims
                            self.timeconvert_psychopy_to_nirstar(
                                float(self.sample_rate),
                                float(NSstim1_t),
                                float(PSstim1_t),
                                float(datum[onset_ind])
                            ),
                            blocks[datum[running_ind]]) # indicates the stimulus column (or block?)
                        )

                    for (stim_time, stim_col) in converted_stims:
                        # make bit format stims
                        evts = [0]*(len(blocks.keys()) + 1) # Generate the event file line structure (right now assuming 2)
                        evts[stim_col]=1 
                        
                        # and write these as lines in correct format for .evt
                        line = str(round(stim_time))
                        for evt_col in evts:
                            line += "\t"
                            line += str(evt_col)
                        line += "\n"
                            
                        output_lines.append(line)
                    
                    # move OG evt to _old.evt
                    if os.path.exists(og_evt.replace(".evt", "_old.evt")):
                        shutil.move(
                            og_evt,
                            og_evt.replace(".evt", "_old.evt"))
                    
                    # write the lines as the new, properly named .evt
                    f = open(og_evt, 'w')
                    
                    for line in output_lines:
                        f.write(line)
                    
                    f.close()
        return

    def timeconvert_psychopy_to_nirstar(self, sample_rate, NSstim1_t, PSstim1_t, PSevent_t):
        NSevent_t = NSstim1_t + (PSevent_t - PSstim1_t) * sample_rate
        return NSevent_t

    def save_master(self):
        final_master = {}
        headers = []
        for subject in self.master.keys():
            for timepoint in self.master[subject].keys():
                for nickname in self.master[subject][timepoint].keys():
                    for header in self.master[subject][timepoint][nickname]:
                        for column_ind, data in enumerate(self.master[subject][timepoint][nickname][header]):
                            
                            column = f'{nickname}_{header}_{column_ind}'
                            if column not in headers:
                                headers.append(column)

                            row = f'{subject}-{timepoint}'
                            if row not in final_master.keys():
                                final_master[row] = {potential_header:None for potential_header in headers}
                            
                            final_master[row][column] = data
                            
                            
        
        dataset = [['Child_ID', 'Time'] + headers]
        for row in final_master.keys():
            data = []
            for header in headers:
                data.append(final_master[row][header])
            dataset.append(row.split('-') + data)

        with open(f'{self.analysis_folder}EmoGrow_Behavioral_Masterfile.csv', 'w') as file:
            csvwriter = csv.writer(file)
            for row in dataset:
                csvwriter.writerow(row)

