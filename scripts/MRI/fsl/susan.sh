#!/bin/bash

# usage: bash susan.sh <list_of_nii_paths>

for f in `cat $1`
do
        echo "Smoothing: $(basename ${f})"
        sbatch /home/claytons/LCBDtools/scripts/MRI/sbatch/fsl_susan_sbatch.sh $f
done
