#!/bin/bash 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(continuumio/anaconda3)'
#BSUB -n 60
#BSUB -R 'rusage[mem=80GB] select[mem>80000 && tmp>250]'

conda init 
source /home/dennys/.bashrc
conda activate lcbd-env

python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/NIRS/hrfunc/CARE_synchrony_deconv.py 
