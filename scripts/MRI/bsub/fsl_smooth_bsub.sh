#!/bin/bash

#SBATCH --job-name fsl_smooth
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=khalilt@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 18:00:00
#SBATCH --output fsl_test.log

pwd; hostname; date

module load FSL

FSLOUTPUTTYPE=NIFTI
export FSLOUTPUTTYPE

fslmaths $1 -s 6 $2