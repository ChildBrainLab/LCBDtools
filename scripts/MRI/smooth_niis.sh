#!/bin/bash

# usage: bash smooth_niis.sh <list_of_nii_paths> <sigma_mm kernel>

for f in `cat $1`
do
	echo "Smoothing: $(basename ${f})"
	sbatch /home/claytons/fsl_smooth_sbatch.sh $f $2 "${f%.*}_smoothed_${2}mm.${f##*.}"
done
