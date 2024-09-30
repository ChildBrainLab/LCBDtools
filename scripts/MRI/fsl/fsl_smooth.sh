#!/bin/bash

#module load FSL

#FSLOUTPUTTYPE=NIFTI
#export FSLOUTPUTTYPE

subject=$1
input_directory=$2/$subject/

for subject_file in `find $input_directory -name '*preproc_bold.nii.gz'`
do
    output_file=${subject_file/'.nii.gz'/'_7mm_smoothed.nii'}

    if [ -f $output_file ]
    then
        echo "$subject already smoothed..."
        continue
    fi
    
    echo "Smoothing $subject..."
    fslmaths $subject_file -s 7 $output_file
done
