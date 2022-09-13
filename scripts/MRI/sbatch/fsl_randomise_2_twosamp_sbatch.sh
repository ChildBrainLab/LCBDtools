#!/bin/bash

#SBATCH --job-name fsl_randomise
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 24:00:00
#SBATCH --output randomise.log

pwd; hostname; date

module load fsl

export OPENBLAS_NUM_THREADS=1

randomise -i $1 -o $2 -d $3 -t $4 -m $5 -T
