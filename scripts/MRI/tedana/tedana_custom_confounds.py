# -*- coding: utf-8 -*-
"""
This will create a new folder and file for each participant/session
Folder: custom_confounds
File: something ending with confounds_timeseries.tsv, matching the name of the fmriprep confound timeseries file

That will be fed into XCP_D

XCP_D is dumb and insists on the custom confounds file having the same name as the default file, just located elsewhere. Whyyyy
"""

import os
import pandas as pd
from glob import glob


#folder where all the tedana files are saved
#I think for RIS this should be something like: 'moochie/analysis/CARE/ME_tedana_data/'
startingfolder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/'

tedanafolder = startingfolder + 'ME_tedana_data/'
fmriprepfolder = startingfolder + 'ME_fMRIPrep_data/'

outputfolder = startingfolder + 'custom_confounds/'

fileofinterest = 'tedana_metrics.tsv'


#if this is True, it will create outputs even if they already exist
replacer = True

#if this is True, it won't actually create outputs. Useful for checking if everything looks reasonable
testmode = False


mixfilelist = []
metfilelist = []
conffilelist = []
subjectlist = []
sessionlist = []
outputlist = []


if os.path.isdir(outputfolder) == False and testmode == False:
    os.makedirs(outputfolder)

#get all tedana metrics files for all participants and all sessions
print("Getting list of all ICA mixing needing relabelled")
print("")
for path, subdirs, files in os.walk(tedanafolder):
    for name in files:
        if name.endswith(fileofinterest):
            #get the path to the tedana metrics file
            
            #apparently windows is dumb and uses both \\ and / to separate folders?
            #I'm trying to split the string to get subject/session info, so let's rename the path so folders
            #are separated in a consistent way
            #probably not necessary on other OS? but probably shouldn't break anything to leave it in
            #I dunno, I'm just testing this on my PC
            
            adjpath = path
            adjpath = adjpath.replace('\\', '/')
            
            #get the subject ID and session number by splitting the path string
            splitpath = adjpath.split('/')
            
            mixfile = adjpath + '/' + splitpath[-2] + '_' + splitpath[-1] + '_desc-ICA_mixing.tsv'
            metfile = adjpath + '/' + splitpath[-2] + '_' + splitpath[-1] + '_desc-tedana_metrics.tsv'
            
            fmripreppath = fmriprepfolder  + splitpath[-2] + '/' + splitpath[-1] + '/'
            print(fmripreppath)
            conffile = glob(f"{fmripreppath}/*/*confounds_timeseries.tsv")
            
            print(f"{os.path.exists(mixfile)} {os.path.exists(metfile)} {len(conffile)}")
            if os.path.exists(mixfile) and os.path.exists(metfile) and len(conffile) == 1:
                if not os.path.exists(outputfolder+conffile[0]) or replacer:
                    mixfilelist.append(mixfile)
                    metfilelist.append(metfile)
                    conffilelist.append(fmripreppath+conffile[0])
                    outputlist.append(outputfolder+conffile[0])
                
                    subjectlist.append(splitpath[-2]) #this should be like "sub-50111" getting added to list
                    sessionlist.append(splitpath[-1]) #this should be like "ses-0" getting added to list
        
print(mixfilelist)
#loop through all files
for n in range(len(mixfilelist)):
    person = subjectlist[n]
    session = sessionlist[n]
    
    mixfile = mixfilelist[n]
    metfile = metfilelist[n]
    conffile = conffilelist[n]
    outputfile = outputlist[n]

    outputfile = outputfolder + outputfile.split('/')[-1]
    print(f"Output file: {outputfile}")

    print("Renaming ICA mixing df columns for",person,session)
    
    # Load the mixing matrix
    mixing_df = pd.read_table(mixfile)  # Shape is time-by-components
    
    # Load the component table
    metrics_df = pd.read_table(metfile)
    
    all_columns = list(metrics_df['Component'])
    rejected_columns = list(metrics_df.loc[metrics_df["classification"] == "rejected", "Component"])
    accepted_columns = list(metrics_df.loc[metrics_df["classification"] == "accepted", "Component"])
    new_column_names = []
    
    bad = False
    
    if len(rejected_columns) == 0 or len(accepted_columns) == 0:
        bad = True
        print("Components not properly classified as accepted or rejected")
    
    for column in all_columns:
        if column in rejected_columns:
            new_column_names.append(column)
        elif column in accepted_columns:
            new_column_names.append('signal__' + column)
        else:
            print("Problem renaming ICs")
            bad = True
    
    if not list(mixing_df.columns) == all_columns:
        print("Problem with column names")
        bad = True
        
    if bad == False:
        mixing_df.columns = new_column_names
        if testmode == False:
            mixing_df.to_csv(outputfile,index=False,sep='\t')
        print("Successfully created",outputfile)
        print("")
            








