#!/bin/bash 
#BSUB -G compute-perlmansusan 
#BSUB -q general-interactive
#BSUB -m general-interactive
#BSUB -a 'docker(continuumio/anaconda3:latest)'
#BSUB -J bsub-tedana
#BSUB -n 16
#BSUB -R 'rusage[mem=24GB] select[mem>24000 && tmp>120]'
#BSUB -oo tedana-output.txt


if [ -f output\out\sub-$SUBJECT\ses-$SESSION\func\sub-${SUBJECT}_ses-${SESSION}_task-movieA_echo-1_desc-preproc_bold.nii.gz ] ; then
    export MOVIE=A
fi

if [ -f output\out\sub-$SUBJECT\ses-$SESSION\func\sub-${SUBJECT}_ses-${SESSION}_task-movieB_echo-1_desc-preproc_bold.nii.gz ] ; then
    export MOVIE=B
fi

if [ -f output\out\sub-$SUBJECT\ses-$SESSION\func\sub-${SUBJECT}_ses-${SESSION}_task-movieC_echo-1_desc-preproc_bold.nii.gz ] ; then
    export MOVIE=C
fi

tedana -d output\out\sub-$SUBJECT\ses-$SESSION\func\sub-${SUBJECT}_ses-${SESSION}_task-movie${MOVIE}_echo-1_desc-preproc_bold.nii.gz \
    output\out\sub-$SUBJECT\ses-$SESSION\func\sub-${SUBJECT}_ses-${SESSION}_task-movie${MOVIE}_echo-2_desc-preproc_bold.nii.gz \
    output\out\sub-$SUBJECT\ses-$SESSION\func\sub-${SUBJECT}_ses-${SESSION}_task-movie${MOVIE}_echo-3_desc-preproc_bold.nii.gz \
    -e 13.2 38.76 64.32 --out-dir tedana_output/ \
    --mask output\out\sub-$SUBJECT\ses-$SESSION\func\sub-${SUBJECT}_ses-${SESSION}_task-movie${MOVIE}_desc-brain_mask.nii.gz \
    --prefix sub-${SUBJECT}_ses-$SESSION