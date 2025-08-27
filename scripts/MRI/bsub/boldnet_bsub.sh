#!/bin/bash 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -M 150000000
#BSUB -a 'docker(continuumio/anaconda3)'
#BSUB -n 60
#BSUB -R 'select[mem>150GB && tmp>150GB] rusage[mem=150GB, tmp=150GB]'

conda init 
source /home/dennys/.bashrc
conda activate lcbd-env

python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/boldnet/main.py

