#!/bin/bash 
#BSUB -G compute-perlmansusan
#BSUB -q general
#BSUB -m general
#BSUB -M 100000000
#BSUB -a 'docker(continuumio/anaconda3)'
#BSUB -n 60
#BSUB -R 'select[mem>100GB && tmp>100GB] rusage[mem=100GB, tmp=100GB]'

JOBFOLDER=`ls /tmp/`
HOMEDIR=`ls /home/`

cd /tmp/$JOBFOLDER/

mkdir /tmp/$JOBFOLDER/ABCD/

WORKDIR=/tmp/$JOBFOLDER/ABCD/

conda init 
source /home/dennys/.bashrc
conda activate lcbd-env

bash /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/boldnet/download_abcd.sh $WORKDIR /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/script/MRI/boldnet/downloaded.txt 2

python3 /storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/boldnet/main_abcd.py