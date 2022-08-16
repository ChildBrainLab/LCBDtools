#!/bin/bash

# usage: bash inverse_masks.sh <list_of_nii_paths>

for f in `cat $1`
do
        ext="${f#*.}"
        fname="${f%.$ext}"
        echo "Inversing: $(basename ${f})"
        sbatch /home/claytons/LCBDtools/scripts/MRI/sbatch/fsl_inversemask_sbatch.sh $f "${fname}_inverse.${ext}"
	#echo $a
done
