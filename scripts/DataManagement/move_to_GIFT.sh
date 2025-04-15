
data="/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/fMRI_data/derivatives/fmriprep/"
new_path="/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE_GIFT/"

for filepath in `find $data -name "*ses-0*MNIPediatricAsym_*7mm_smoothed.nii"` ;
do
    if [[ "$filepath" != "*copy*" ]]
    then
        dir=$(dirname "$filepath")
        file=$(basename "$filepath")

        new_dir=$(echo "$filepath" | cut -d '/' -f12)

        mkdir -p $new_path$new_dir/
        
        mv $filepath $new_path$new_dir/4D.nii
    fi
done
