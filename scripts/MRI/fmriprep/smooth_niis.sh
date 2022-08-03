#!/bin/bash

# usage: bash smooth_niis.sh <list_of_nii_paths> <sigma_mm kernel>

for f in `cat $1`
do
	ext="${f#*.}"
	fname="${f%.$ext}"
	echo "Smoothing: $(basename ${f})"
	sbatch /home/claytons/LCBDtools/scripts/MRI/sbatch/fsl_smooth_sbatch.sh $f $2 "${fname}_smoothed_${2}mm.${ext}"
done
