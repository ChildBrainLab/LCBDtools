#!/bin/bash

export DATE=$(date +'%m-%d')

export LSF_DOCKER_PRESERVE_ENVIRONMENT=true

export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active /home/$USER:/home/$USER"

export FSLDIR=/usr/local/fsl
export PATH=$FSLDIR/bin:$PATH
export FSLMULTIFILEQUIT=TRUE
export FSLOUTPUTTYPE=NIFTI_GZ

bsub -J smoothing -oo logs/fsl/smoothing_$DATE.log -g /$USER/preprocessing < smooth_bsub.sh

