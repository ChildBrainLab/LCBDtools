#!/bin/bash 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(continuumio/anaconda3)'
#BSUB -n 4
#BSUB -R "select[mem>30000]"

conda init 
source /home/dennys/.bashrc
conda activate lcbd-env

python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/tedana_data_summary.py

python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/tedana_motion_summary.py

python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/tedana_custom_confounds.py 