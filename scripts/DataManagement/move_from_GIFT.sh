
data="/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/fMRI_data/derivatives/fmriprep/"
new_path="/storage1/fs1/perlmansusan/Active/moochie/user_data/khalilt/CARE_GIFT/"

for filepath in `find $data -name "*MNIPediatricAsym_*-preproc_bold.nii"` ;
do
    if [[ "$filepath" != "*copy*" ]]; then
        dir=$(dirname "$filepath")
        file=$(basename "$filepath")

        if [[ "$file" == *"movieA"* ]]; then
            movie="movieA"
        elif [[ "$file" == *"movieB"* ]]; then
            movie="movieB"
        else
            movie="movieC"
        fi

        subject=$(echo "$filepath" | cut -d '/' -f12)
        session=$(echo "$filepath" | cut -d '/' -f13)    

        old_dir=$(echo "$filepath" | cut -d '/' -f12)

        for newfile in `find $new_path$subject/ses-0/func/ -name '4D.nii'` ;
        do
            filename="${subject}_${session}_task-${movie}_space-MNIPediatricAsym_cohort-2_res-2_desc-preproc_bold_7mm_smoothed.nii"

            mv $newfile "$data$subject/$session/func/$filename"
        done
    fi
done