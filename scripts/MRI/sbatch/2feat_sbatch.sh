#!/bin/bash

#SBATCH --job-name fsl_2
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

feat /scratch/claytons/MRI_data_clean/derivatives/fmriprep/second_level.feat/second_level_FE.fsf 
