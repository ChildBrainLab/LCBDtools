#!/bin/bash

# usage: bash crop_volumes.sh <list_of_nii_paths>

for f in `cat $1`
do
        ext="${f#*.}"
        fname="${f%.$ext}"
        echo "Cropping: $(basename ${f})"
	let a=$(fslnvols $f)-2
        sbatch /home/claytons/LCBDtools/scripts/MRI/sbatch/fsl_crop_sbatch.sh $f "${fname}_cropped.${ext}" 1 $a
	#echo $a
done
