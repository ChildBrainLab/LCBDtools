#!/bin/sh

# export OUTPUT_DIRS
export CONDA_ENVS_DIRS="/storage1/fs1/perlmansusan/Active/moochie/resources/conda/envs/"
export CONDA_PKGS_DIRS="/storage1/fs1/perlmansusan/Active/moochie/resources/conda/pkgs/"

export BOLDNET_DIR="/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/boldnet/"

export PATH="/opt/conda/bin:$PATH"
export PYTHONPATH='/storage1/fs1/perlmansusan/Active/moochie/github/BOLDnet:/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/boldnet':$PYTHONPATH

export LSF_DOCKER_VOLUMES="/storage1/fs1/perlmansusan/Active:/storage1/fs1/perlmansusan/Active /home/$USER:/home/$USER"

export LSF_DOCKER_PRESERVE_ENVIRONMENT=true

export DATE=$(date +'%m-%d')

bsub -J boldnet-$DATE -oo $BOLDNET_DIR/logs/boldnet_$DATE.log -g /$USER/preprocessing < /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/bsub/boldnet_bsub.sh
