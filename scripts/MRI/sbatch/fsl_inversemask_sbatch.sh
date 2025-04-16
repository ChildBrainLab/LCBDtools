#!/bin/bash

#SBATCH --job-name fsl_inverse_mask
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 10G
#SBATCH --time 01:00:00
#SBATCH --output fsl_inverse.log

pwd; hostname; date

module load fsl

FSLOUTPUTTYPE=NIFTI_GZ
export FSLOUTPUTTYPE

fslmaths $1 -mul -1 -add 1 $2
