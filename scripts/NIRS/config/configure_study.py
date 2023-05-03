import os, json

study_name = '_'.join(input('What is the name of the study?').split(' '))

config = {}
config['data folder'] = input('Where does the study data live?') 
config['task_folder'] = input('Where does the task data live?')
config['task'] = input('Which tasks are involved in the study?')
config['participant_num_len'] = input('How many participants are involved?')
config['ex_subs'] = input('Which subjects should be excluded?')
config['in_subs'] = input('Would you like to exlusively run the pipeline on a subset of the subject pool?')
