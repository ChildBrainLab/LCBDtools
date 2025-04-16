#!/bin/bash

#SBATCH --job-name fsl_test
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 12:00:00
#SBATCH --output fsl_test.log
pwd; hostname; date

module load fsl

feat /scratch/claytons/chpctransfer/chpc_template.fsf 
