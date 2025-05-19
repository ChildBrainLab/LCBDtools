#!/bin/bash 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -a 'docker(continuumio/anaconda3)'
#BSUB -n 16
#BSUB -R 'rusage[mem=30GB] select[mem>30000 && tmp>250]'

conda init 
source /home/dennys/.bashrc
conda activate lcbd-env

#python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/analysis/ROI_avg.py 
python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/analysis/ROI_std.py 
#python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/analysis/ROI_corr.py 