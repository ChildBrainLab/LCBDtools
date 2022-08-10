#!/bin/bash

#SBATCH --job-name fsl_feat
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 12:00:00
#SBATCH --output feat.log

pwd; hostname; date

module load fsl

fsl_sub feat /scratch/claytons/MRI_data_clean/derivatives/fmriprep/$1/feat_script.fsf 
