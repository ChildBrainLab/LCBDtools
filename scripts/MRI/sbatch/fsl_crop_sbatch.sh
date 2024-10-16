#!/bin/bash

#SBATCH --job-name fsl_crop
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 18:00:00
#SBATCH --output fsl_crop.log

pwd; hostname; date

module load fsl

FSLOUTPUTTYPE=NIFTI
export FSLOUTPUTTYPE

fslroi $1 $2 $3 $4
