#!/bin/bash
#BSUB -G compute-perlmansusan 
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(continuumio/anaconda3:latest)'
#BSUB -n 16
#BSUB -R 'rusage[mem=30GB] select[mem>30000 && tmp>200]'

JOBFOLDER=`ls /tmp/`
HOMEDIR=`ls /home/`

# Activate lcbd environment
conda init 
source /home/$HOMEDIR/.bashrc
conda activate lcbd-env

# Define storage allocations areas of interest
STORAGE_ALLOCATION=/storage1/fs1/perlmansusan/Active/
OUTPUT_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_fMRIPrep_data/
TEDANA_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_tedana_data/
LICENSE_DIR=${STORAGE_ALLOCATION}moochie/github/LCBDtools/scripts/MRI/fmriprep/

# Define our conda environment variables
FMRIPREP_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_fMRIPrep_data/
TEDANA_TEMP_DIR=/tmp/$JOBFOLDER/
TEDANA_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_tedana_data/


cd /tmp/$JOBFOLDER/
mkdir -p $TEDANA_DIR/sub-$SUBJECT/

declare -a SESSIONS=(0 1 2)

for SESSION in "${SESSIONS[@]}"
do
    mkdir -p $TEDANA_TEMP_DIR/sub-$SUBJECT/ses-$SESSION/

    if [ -f $FMRIPREP_DIR/sub-$SUBJECT/ses-$SESSION/func/sub-${SUBJECT}_ses-${SESSION}_task-movieA_echo-1_desc-preproc_bold.nii ] ; then
        export MOVIE=A
    fi

    if [ -f $FMRIPREP_DIR/sub-$SUBJECT/ses-$SESSION/func/sub-${SUBJECT}_ses-${SESSION}_task-movieB_echo-1_desc-preproc_bold.nii ] ; then
        export MOVIE=B
    fi

    if [ -f $FMRIPREP_DIR/sub-$SUBJECT/ses-$SESSION/func/sub-${SUBJECT}_ses-${SESSION}_task-movieC_echo-1_desc-preproc_bold.nii ] ; then
        export MOVIE=C
    fi

    mkdir -p $TEDANA_DIR/sub-$SUBJECT/ses-$SESSION/

    tedana -d $FMRIPREP_DIR/sub-$SUBJECT/ses-$SESSION/func/sub-${SUBJECT}_ses-${SESSION}_task-movie${MOVIE}_echo-1_desc-preproc_bold.nii \
        $FMRIPREP_DIR/sub-$SUBJECT/ses-$SESSION/func/sub-${SUBJECT}_ses-${SESSION}_task-movie${MOVIE}_echo-2_desc-preproc_bold.nii \
        $FMRIPREP_DIR/sub-$SUBJECT/ses-$SESSION/func/sub-${SUBJECT}_ses-${SESSION}_task-movie${MOVIE}_echo-3_desc-preproc_bold.nii \
        -e 13.2 38.76 64.32 --out-dir $TEDANA_TEMP_DIR/sub-$SUBJECT/ses-$SESSION/ \
        --mask $FMRIPREP_DIR/sub-$SUBJECT/ses-$SESSION/func/sub-${SUBJECT}_ses-${SESSION}_task-movie${MOVIE}_desc-brain_mask.nii \
        --prefix sub-${SUBJECT}_ses-$SESSION

    cp -r $TEDANA_TEMP_DIR/sub-$SUBJECT/ $TEDANA_DIR/

    for gzfile in `find $TEDANA_DIR/sub-$SUBJECT/ses-$SESSION/ -name "*.gz"`
    do
        gzip -d $gzfile
    done
done

bash 
