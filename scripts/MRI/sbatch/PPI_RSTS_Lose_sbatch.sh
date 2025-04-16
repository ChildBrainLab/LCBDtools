#!/bin/bash

#SBATCH --job-name PPI_setup
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=khalilt@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 01:00:00
#SBATCH --output PPI_setup.log

cd /home/khalilt/script_practice/
ml matlab

matlab -nodisplay -nosplash -r "PPI_RSTS_Lose_sub $1"

