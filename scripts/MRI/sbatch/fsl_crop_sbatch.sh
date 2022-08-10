#!/bin/bash

#SBATCH --job-name fsl_smooth
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 18:00:00
#SBATCH --output fsl_test.log

pwd; hostname; date

module load fsl

FSLOUTPUTTYPE=NIFTI
export FSLOUTPUTTYPE

fslroi $1 $2 $2 $3
