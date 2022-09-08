#!/bin/bash

#SBATCH --job-name fsl_mask
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

FSLOUTPUTTYPE=NIFTI_GZ
export FSLOUTPUTTYPE

cope=$1
mask=$2

# multiply cope by mask and save to new file with cope
echo "Masking: $(dirname $(dirname  ${mask}))"
#fslmaths $cope -mas $mask "${cope%%.*}"_masked."${cope#*.}"
fslmaths $cope -mas $mask "${cope%%.nii.gz}"_masked."${cope#*.*.}"
