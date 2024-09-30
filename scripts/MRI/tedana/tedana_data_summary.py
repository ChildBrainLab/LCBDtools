# -*- coding: utf-8 -*-
"""
Spyder Editor

Tedana data summary
"""

import pandas as pd
import os


#folder where all the tedana files are saved
#I think for RIS this should be something like: 'moochie/analysis/CARE/ME_tedana_data/'
startingfolder = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_tedana_data/'

#where to save the output file
outputfile = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_tedana_data/summarydf.csv'


fileofinterest = 'tedana_metrics.tsv'


filelist = []
subjectlist = []
sessionlist = []

#get all tedana metrics files for all participants and all sessions
for path, subdirs, files in os.walk(startingfolder):
    for name in files:
        if name.endswith(fileofinterest):
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
            subjectlist.append(splitpath[-2]) #this should be like "sub-50111" getting added to list
            sessionlist.append(splitpath[-1]) #this should be like "ses-0" getting added to list

numics = []
numicsaccepted = []
numicsrejected = []
percenticsaccepted = []

varexpacceptedic = []
varexprejectedic = []
vartotal = []
percentvaraccepted = []

normvarexpacceptedic = []
normvarexprejectedic = []
normvartotal = []
normpercentvaraccepted = []


#for each file, get a bunch of summary stats
#hopefully these are useful ones! I have no idea what you'd look at :/
for file in filelist:
    df = pd.read_csv(file,sep='\t')
    acceptdf = df[df['classification'] == 'accepted']
    rejectdf = df[df['classification'] == 'rejected']
    
    
    #length of the df is the number of independent components    
    numics.append(len(df))
    numicsaccepted.append(len(acceptdf))
    numicsrejected.append(len(rejectdf))
    percenticsaccepted.append(len(acceptdf)/len(df)*100)
    
    #variance explained: in total, of accepted/rejected components, and percent accepted out of total
    vartotal.append(sum(df['variance explained']))
    varexpacceptedic.append(sum(acceptdf['variance explained']))
    varexprejectedic.append(sum(rejectdf['variance explained']))
    percentvaraccepted.append(sum(acceptdf['variance explained'])/sum(df['variance explained'])*100)
    
    #normalized variance explained: in total, of accepted/rejected components, and percent accepted out of total
    normvartotal.append(sum(df['normalized variance explained']))
    normvarexpacceptedic.append(sum(acceptdf['normalized variance explained']))
    normvarexprejectedic.append(sum(rejectdf['normalized variance explained']))
    normpercentvaraccepted.append(sum(acceptdf['normalized variance explained'])/sum(df['normalized variance explained'])*100)
       

#create summarydf
summarydf = pd.DataFrame({
    'subject':subjectlist,
    'session':sessionlist,
    'numIC':numics,
    'numIC_accept':numicsaccepted,
    'numIC_reject':numicsrejected,
    'percentICaccept':percenticsaccepted,
    'totalvariance':vartotal,
    'totalvariance_accept':varexpacceptedic,
    'totalvariance_reject':varexprejectedic,
    'percentvarianceaccept':percentvaraccepted,
    'totalnormvariance':normvartotal,
    'totalnormvariance_accept':normvarexpacceptedic,
    'totalnormvariance_reject':normvarexprejectedic,
    'percentnormvarianceaccept':normpercentvaraccepted,    
    })

#sort file
summarydf = summarydf.sort_values(by=['subject','session'])

#savefile
summarydf.to_csv(outputfile)



