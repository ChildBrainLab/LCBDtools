#!/bin/bash

# usage: bash placeblablabla.sh /path/to/bids/dir

bidsdir=$1

for sub in `/bin/ls -d $bidsdir/derivatives/fmriprep/sub*/ses-0/func/ | grep smoothed | grep .nii.gz`
do
	# the case that there are smoothed .nii files here
	if [[ $(/bin/ls -d $(dirname $sub) | grep smoothed | grep -v .nii.gz | grep .nii) ]]; then
		echo "Already done"
	# the case there are not unzipped smoothed niftis
	else
		echo "Unzipping: $(basename $sub)" 
		sbatch /home/claytons/LCBDtools/scripts/MRI/sbatch/gunzip.sh $sub
	fi
done

