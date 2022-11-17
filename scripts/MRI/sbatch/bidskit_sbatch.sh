#!/bin/bash

#SBATCH --job-name bidskit_p2
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=khalilt@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 12:00:00
#SBATCH --output bidskit_p2.log


source activate LCBDenv

bidskit -d $1 --clean-conv-dir --no-anon --subject $2
