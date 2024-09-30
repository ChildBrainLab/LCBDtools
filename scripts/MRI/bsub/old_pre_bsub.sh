#!/bin/sh

SUBJECT=$1

STORAGE_ALLOCATION=/storage1/fs1/perlmansusan/Active/
BIDS_DIR=${STORAGE_ALLOCATION}moochie/study_data/CARE/MRI_data/
SCRATCH_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_scratch/
OUTPUT_DIR=${STORAGE_ALLOCATION}moochie/analysis/CARE/ME_fMRIPrep_data/
LICENSE_DIR=${STORAGE_ALLOCATION}moochie/github/LCBDtools/scripts/MRI/fmriprep/

# export OUTPUT_DIRS
export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan:/storage1/fs1/perlmansusan ${BIDS_DIR}:/input ${SCRATCH_DIR}:/scratch ${OUTPUT_DIR}:/output ${LICENSE_DIR}:/freesurfer"
export LSF_DOCKER_PRESERVE_ENVIRONMENT=true

bsub -n 8 -G compute-perlmansusan -oo fmriprep-output.txt -a 'docker(nipreps/fmriprep)' /bin/bash /input /output/out participant --participant-label $SUBJECT -w /scratch --fs-license-file /freesurfer/license.txt
