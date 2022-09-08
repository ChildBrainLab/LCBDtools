#!/bin/bash

for sub in `cat $1`
do 
	fsleyes render -of $(basename $(dirname $(dirname $(dirname $(dirname $(dirname $sub)))))).png \
	/scratch/claytons/tlbx/templateflow/tpl-MNIPediatricAsym/cohort-2/tpl-MNIPediatricAsym_cohort-2_res-2_T1w.nii.gz \
	$sub -cm red-yellow
done
