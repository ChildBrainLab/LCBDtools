#!/bin/bash


export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active /home/$USER:/home/$USER"

export LSF_DOCKER_PRESERVE_ENVIRONMENT=true

export FSLOUTPUTTYPE=NIFTI_GZ

export FSLDIR=/usr/local/fsl

export PATH=$FSLDIR/bin:$PATH

export OUTPUT_DIR=/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/MRI_data/

bsub -g /$USER/preprocessing < movie_regressor_bsub.sh

bsub -g /$USER/preprocessing < confounds_bsub.sh