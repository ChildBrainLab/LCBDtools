#!/bin/bash

module load FSL

FSLOUTPUTTYPE=NIFTI
export FSLOUTPUTTYPE

for sub in `cat subject_list.txt | shuf` # Run through new list of subject to smooth
do 
	echo $sub
	bash moochie/github/LCBDtools/scripts/MRI/fsl/fsl_smooth.sh $sub moochie/analysis/CARE/MRI_data/derivatives/fmriprep/ 
done
