rsync -r . claytons@login3.chpc.wustl.edu:/scratch/claytons/MRI_data_clean/derivatives/fmriprep --include "sub-*/ses-*/func/*" --exclude "*sourcedata*" --update -aav
