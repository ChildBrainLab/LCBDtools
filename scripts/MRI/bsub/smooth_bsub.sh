#!/bin/bash
#BSUB -G compute-perlmansusan 
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(diannepat/fsl6)'
#BSUB -n 8
#BSUB -R 'rusage[mem=16GB] select[mem>16000 && tmp>40]'

export FSLDIR=/usr/local/fsl
export PATH=$FSLDIR/bin:$PATH
export FSLMULTIFILEQUIT=TRUE
export FSLOUTPUTTYPE=NIFTI_GZ

directory=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/fMRI_data/derivatives/fmriprep/

for subject in `find $directory -type d -name  'sub-*' | shuf`
do
    echo $subject
    subject_id=basename $subject
    for session in `find $subject -type d -name 'ses-*'`
    do
        echo $session
        session_id=basename $session
        for subject_file in `find $session/ -name  '*bold.nii'` #'*desc-preproc_bold.nii'`
        do
            echo $subject_files
            output_file=${subject_file/'.nii'/'_6mm_smoothed.nii'}

            if [ -f $output_file ]
            then
                continue
            fi

            echo "Smoothing $session with 6mm kernel..."
            fslmaths $subject_file -s 6 $output_file

            gzip -d $output_file

            output_file=${subject_file/'.nii'/'_7mm_smoothed.nii'}

            if [ -f $output_file ]
            then
                continue
            fi

            echo "Smoothing $session with 7mm kernel..."
            fslmaths $subject_file -s 7 $output_file

            gzip -d $output_file
        done
    done
done

echo $FSLDIR
echo 'Something...'