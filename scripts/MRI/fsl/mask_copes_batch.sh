#!/bin/bash

# usage: mask_copes.sh /path/to/list/of/copes
# <path/to/first_level.feat/stats/>

# get path of cope1.nii.gz
for cope in `cat $1`
do
	# get path of mask
	#mask=$(dirname $(dirname $cope))/$(ls $(dirname $(dirname $cope)) | grep mask.nii.gz)
	mask=$(dirname $(dirname $(dirname $cope)))/$(ls $(dirname $(dirname $(dirname $cope))) | grep mask.nii.gz)

	# run sbatch fsl maths multiple cope by mask
	sbatch /home/claytons/LCBDtools/scripts/MRI/sbatch/fsl_mask_sbatch.sh $cope $mask

done
