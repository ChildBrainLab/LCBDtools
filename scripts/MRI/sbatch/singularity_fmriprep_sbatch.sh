#!/bin/bash

#SBATCH --job-name fmriprep
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 8
#SBATCH --mem 60G
#SBATCH --time 18:00:00
#SBATCH --output fmriprep.log

pwd; hostname; date

bash /home/claytons/LCBDtools/scripts/MRI/fmriprep_ss_sb_singularity.sh $1 $2
