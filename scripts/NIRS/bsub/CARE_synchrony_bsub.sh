#!/bin/bash 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(continuumio/anaconda3)'
#BSUB -n 100
#BSUB -R "select[mem>70000]"

conda init 
# source /home/dennys/.bashrc
source /storage1/fs1/perlmansusan/Active/moochie/local/bashrc
conda activate lcbd-env

python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/NIRS/analysis/CARE_synchrony.py 
