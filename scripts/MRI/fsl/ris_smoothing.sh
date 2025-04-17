FSLOUTPUTTYPE=NIFTI
export FSLOUTPUTTYPE


for sub in /storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/MRI_data/derivatives/fmriprep/sub*/ses*/func/*preproc_bold.nii.gz; do

	funcdir=$(dirname $sub)
	funcname=$(basename $sub)
	smoothed=${funcname%.nii.gz}_7mm_smoothed.nii

	if ! [[ -f $funcdir/$smoothed ]]; then
		
		echo $smoothed
		fslmaths $funcdir/$funcname -s 7 $funcdir/$smoothed

	fi

done

