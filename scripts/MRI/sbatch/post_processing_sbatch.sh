#!/bin/bash

#SBATCH --job-name fsl_mask
#SBATCH --mail-type=END,FAIL 
#SBATCH --mail-user=claytons@wustl.edu
#SBATCH --nodes 1
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 4
#SBATCH --mem 60G
#SBATCH --time 18:00:00
#SBATCH --output fsl_test.log

BIDSdir=$1
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# extract fmriprep confounds into their own .txt file regressor for each functional scan available in the BIDS directory
python3 $SCRIPT_DIR/../fmriprep/extract_confounds.py $BIDSdir

# put cropped versions of movie regressors for any potentially truncated fMRI runs in each of the functional folders
bash place_cropped_movie_regs.sh $BIDSdir

# for any functional run, do the 7mm gauss smoothed with FSL, exporting as NII, not GZ
for sub in /scratch/claytons/MRI_data_clean/derivatives/fmriprep/sub*/ses*/func/*preproc_bold.nii.gz; do

	funcdir=$(dirname $sub)
	funcname=$(basename $sub)
	smoothedname=${funcname%.nii.gz}_7mm_smoothed.nii

	# if the smoothed file does not already exist
	if ! [[ -f $fundir/$smoothedname ]]; then
		
		# submit the sbatch job which smoothes and exports as .nii
		sbatch $SCRIPT_DIR/fsl_smooth_sbatch.sh $funcdir/$funcname $funcdir/$smoothedname

	fi
