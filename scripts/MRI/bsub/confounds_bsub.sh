#!/bin/bash
#BSUB -G compute-perlmansusan 
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(continuumio/anaconda3)'
#BSUB -J fmriprep-regressors
#BSUB -n 4
#BSUB -R 'rusage[mem=10GB] select[mem>9000 && tmp>60]'
#BSUB -oo logs/post_processing/confound-regressors.log

LCBDtools=/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/
HOME=/home/dennys

# extract fmriprep confounds into their own .txt file regressor for each functional scan available in the BIDS directory
OUTPUT_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_XCP_kirk_data/
python3 $LCBDtools/scripts/MRI/fmriprep/extract_confounds.py $OUTPUT_DIR

OUTPUT_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_XCP_kirk_data_2/
python3 $LCBDtools/scripts/MRI/fmriprep/extract_confounds.py $OUTPUT_DIR

OUTPUT_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ME_XCP_khalil_data/
python3 $LCBDtools/scripts/MRI/fmriprep/extract_confounds.py $OUTPUT_DIR

OUTPUT_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/MRI_data/
python3 $LCBDtools/scripts/MRI/fmriprep/extract_confounds.py $OUTPUT_DIR
