#!/bin/bash

# downloadCNDASessions.sh expects 2 params
# CNDA user id
# input csv file format:  project,subject,exp
#  example file line:  proj_A,subj001,subj0001_MR1
# example:  ./downloadCNDASessions.sh userID /pathToMyFile/myListOfSessions.txt

INPUT_FILE=$2
USER=$1
SITE=https://cnda.wustl.edu
CURR_DIR=`pwd`

JSESSION=`curl -u ${USER} "${SITE}/data/JSESSION"`

#!! Update this with directory where sessions should be stored.
SESSIONS_DIR=./CNDA_download_repo
# if [ ! -d ${SESSIONS_DIR} ]; then
#    mkdir ${SESSIONS_DIR}
# fi

let i=1
while read line
do
    let i=$i+1
    echo Downloading ${i} ${line}
    proj=`echo $line | cut -d, -f2`
    subj=`echo $line | cut -d, -f3`
    exp=`echo $line | cut -d, -f4`
    # Option 1: Download all files in the session
    curl -b JSESSIONID=${JSESSION} "${SITE}/data/archive/projects/${proj}/subjects/${subj}/experiments/${exp}/scans/*/files?format=zip" > ${SESSIONS_DIR}/${exp}.zip
    # Option 2: Download specific scans by name (be sure to encode spaces as %20)
    # curl -b JSESSIONID=${JSESSION} "${SITE}/data/archive/projects/${proj}/subjects/${subj}/experiments/${exp}/scans/MPRAGE%20GRAPPA2/files?format=zip" > ${SESSIONS_DIR}/${exp}.zip
    # Option 3: Download specific scans by number (comma-separated for multiple scans)
    # curl -b JSESSIONID=${JSESSION} "${SITE}/data/archive/projects/${proj}/subjects/${subj}/experiments/${exp}/scans/2,3/files?format=zip" > ${SESSIONS_DIR}/${exp}.zip

    #!! If you don't want script to unzip sessions and remove zip file for you, comment lines below
    # cd ${SESSIONS_DIR}
    # unzip ${exp}.zip
    # rm ${exp}.zip
    # cd ${CURR_DIR}
    #!! End commentable block
done < $INPUT_FILE

curl -b JSESSIONID=${JSESSION} -X DELETE "${SITE}/data/JSESSION"
