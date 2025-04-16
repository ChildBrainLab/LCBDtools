#!/bin/bash

#SBATCH --job-name fsl_merge
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 24:00:00
#SBATCH --output feat.log

pwd; hostname; date

module load fsl

export OPENBLAS_NUM_THREADS=1

fslmerge -t $1 $(cat $2) 
