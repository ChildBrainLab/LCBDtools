# -*- coding: utf-8 -*-
"""
Spyder Editor

Tedana data summary
"""

import pandas as pd
import numpy as np
import os


#folder where all the tedana files are saved
#I think for RIS this should be something like: 'moochie/analysis/CARE/ME_tedana_data/'
startingfolder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_fMRIPrep_data/'

#where to save the output file
outputfile = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_tedana_data/summarydf_motion.csv'


fileofinterest = 'framewise_displacement.txt'


filelist = []
subjectlist = []
sessionlist = []
tasklist = []

#get all tedana metrics files for all participants and all sessions
for path, subdirs, files in os.walk(startingfolder):
    for name in files:
        if name.endswith(fileofinterest):

            filename = name.split('/')[-1]
            if filename[:2] == '._':
                continue

            #get the path to the tedana metrics file, and add it to the list
            filelist.append(os.path.join(path,name))
            
            #apparently windows is dumb and uses both \\ and / to separate folders?
            #I'm trying to split the string to get subject/session info, so let's rename the path so folders
            #are separated in a consistent way
            #probably not necessary on other OS? but probably shouldn't break anything to leave it in
            #I dunno, I'm just testing this on my PC
            adjpath = path
            adjpath = adjpath.replace('\\', '/')
            
            #get the subject ID and session number by splitting the path string
            splitpath = adjpath.split('/')
            subjectlist.append(splitpath[-3]) #this should be like "sub-50111" getting added to list
            sessionlist.append(splitpath[-2]) #this should be like "ses-0" getting added to list
            
            splitname = name.split('_')
            for subname in splitname:
                if 'task' in subname:
                    tasklist.append(subname)
            

lenfilelist = []
avgmotionlist = []
numcensoredlist = []
numcensoredlist50 = []



#for each file, get a bunch of summary stats
#hopefully these are useful ones! I have no idea what you'd look at :/
for file in filelist:
    filename = file.split('/')[-1]
    if filename[:2] == '._':
        continue

    motionvals = []
    f = open(file, "r")
    for x in f:
        motionvals.append(float(x))
    
    lenfile = len(motionvals)
    avgmotion = np.mean(motionvals)
    
    highmotionvals = [x for x in motionvals if x > 0.3]
    censor = len(highmotionvals)/len(motionvals)
    
    highmotionvals50 = [x for x in motionvals if x > 0.5]
    censor50 = len(highmotionvals50)/len(motionvals)    
    
    lenfilelist.append(lenfile)
    avgmotionlist.append(avgmotion)
    numcensoredlist.append(censor)
    numcensoredlist50.append(censor50)

#create summarydf
summarydf = pd.DataFrame({
    'subject':subjectlist,
    'session':sessionlist,
    'task':tasklist,
    'len':lenfilelist,
    'avgmotion':avgmotionlist,
    'numcensored':numcensoredlist,
    'numcensored50':numcensoredlist50,
    })

#sort file
summarydf = summarydf.sort_values(by=['subject','session'])

#print(summarydf.to_string())

#savefile
summarydf.to_csv(outputfile)



