import sys, os, random, nilearn
from glob import glob
import nibabel as nib
from nilearn import datasets
from nilearn.image import math_img, load_img, resample_to_img
from nilearn.plotting import plot_roi
from nilearn.masking import apply_mask
import numpy as np

# Define runtime variables defining where data is and where to output results
output_dir = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ROI_averages/'
input_dir = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/fMRI_data/derivatives/fmriprep/'
deviation_dir = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ROI_deviation/'

# Region of interest structure for storing intermediary data
ROI_temp = {'masks': []}

ROIs = { # Define regions of interest (ROI)
    'bed nucleus of the stria terminalis': {'masks': []},
    'paraventricular nucleus': {'masks': []},
    'dorsomedial prefrontal': {'masks': []},
    'temporoparietal junction': {'masks': []},
    'ventromedial prefrontal': {'masks': []},
    'orbitofrontal_cortex': {'masks': []},
    'ventrolateral prefrontal': {'masks': []},
    'anterior cingulate': {'masks': []},
    'anterior insula': {'masks': []},
    'amygdala': {'masks': []},
    'hippocampus': {'masks': []}
}

# Load Harvard-Oxford cortical atlas
cortex_data = datasets.fetch_atlas_harvard_oxford('cort-maxprob-thr25-2mm')
cortex_img = cortex_data.maps
cortex_labels = cortex_data.labels
cortex_atlas = {
    'dorsomedial prefrontal': [3, 25, 28], # Superior frontal gyrus, frontal medial cortex, paracingulate gyrus (dmpfc wall?)
    'temporoparietal junction': [10, 20, 21], # Superior temporal gyrus posterior division, supramarginal gyrus posterior division, angular gyrus (13, temporooccipital part not included)
    'ventromedial prefrontal': [25, 27], # Frontal medial cortex (included again), subcallosal cortex
    'orbitofrontal_cortex': [33], # Frontal orbital cortex
    'ventrolateral prefrontal': [5, 6], # Inferior frontal gyrus (pars triangularis), Inferior Frontal Gyrus (pars opercularis)
    'anterior cingulate': [28, 29], # Cingulate gyrus (anterior division), paracingulate gyrus
    'anterior insula': [2, 6, 41] # Insular cortex, inferior frontal gyrus (pars opercularis), frontal opercular cortex
}
print(f"Cortex Atlas: {cortex_atlas.items()}")

for key, values in cortex_atlas.items():
    for value in values:
        mask = math_img(f'img == {value}', img = cortex_img)
        ROIs[key]['masks'].append(mask) 

# Load Harvard-Oxford subcortical atlas
sub_data = datasets.fetch_atlas_harvard_oxford('sub-maxprob-thr25-2mm')
sub_img = sub_data.maps
sub_labels = sub_data.labels
sub_atlas = {
    'amygdala': [10, 20], # Left and right amygdala
    'hippocampus': [9, 19] # Left and right hippocampus
}

for key, values in sub_atlas.items():
    for value in values:
        mask = math_img(f'img == {value}', img = sub_img)
        ROIs[key]['masks'].append(mask) 
    print(f"Updated ROI: {ROIs[key]}")

# Load custom BNST (Avery et al., 2014) and PVN (Zhang et al., 2017) masks
ROIs['bed nucleus of the stria terminalis']['masks'].append(nib.load('/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/analysis/custom_bnst_mask.nii'))
ROIs['paraventricular nucleus']['masks'].append(nib.load('/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/analysis/custom_pvn_mask.nii'))

# Define movies being analyzed
movies = {
    'A': 1605,
    'B': 1705,
    'C': 1653
}

print(f"ROIs")
for key, value in ROIs.items():
    print(f"{key}: {value}")

_overwrite = False
# Iterate through movies
for movie in movies: # For each movie

    roi_list = list(ROIs.keys())
    random.shuffle(roi_list)

    for roi in roi_list: # Iterate through ROIs
        print(f"movie{movie}-{roi}")
        roi_name = '-'.join(roi.split(' '))
        
        # Grab the ROI movies pre-calculated average and standard deviation
        if os.path.exists(f"{output_dir}movie{movie}_{roi_name}_average_timecourse.npy") == False and os.path.exists(f"{output_dir}movie{movie}_{roi_name}_std_timecourse.npy") == False:
            print(f"movie{movie}-{roi_name} average and standard deviation not calculated yet")
            continue

        roi_avg = np.load(f"{output_dir}movie{movie}_{roi_name}_average_timecourse.npy")
        roi_std = np.load(f"{output_dir}movie{movie}_{roi_name}_std_timecourse.npy")

        masks = ROIs[roi]['masks'] # Grab the ROI mask

        subject_files = glob(f"{input_dir}sub-*/ses-0/func/sub-*_ses-0_task-movie{movie}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_7mm_smoothed.nii") # Grab all subjects for movie
        random.shuffle(subject_files)

        for subject_file in subject_files:
            # Grab subject directory
            subject_dir = subject_file.split('/')[-4]

            # Create name for mask
            roi_dev_filename = f"{deviation_dir}{subject_dir}/ses-0/{subject_dir}_ses-0_roi-{roi_name}_deviation.npy"

            # Check if file exists and remove if needed
            if os.path.exists(roi_dev_filename) and _overwrite == False:
                print(f"Already calculated, skipping {roi_dev_filename}...")
                continue
            elif os.path.exists(roi_dev_filename) and _overwrite == True:
                print(f"Recalculating {roi_dev_filename}...")
                os.remove(roi_dev_filename)

            # Load their data
            image = nib.load(subject_file)

            mask_rois = []
            for mask in masks:# Iterate through masks
                print(f"Calculating {subject_file} standard deviation from ROI {roi_name}...")

                # Skip if average already calculated
                if os.path.exists(roi_dev_filename) and _overwrite == False:
                    print(f"Already calculated, skipping {roi_dev_filename}...")
                    continue
                elif os.path.exists(roi_dev_filename) and _overwrite == True:
                    os.remove(roi_dev_filename)

                # Resample mask to the subjects space
                resampled_mask = nilearn.image.resample_to_img(mask, image, interpolation = 'nearest')

                # Apply mask to get (n_timepoints x n_voxels)
                masked_data = nilearn.masking.apply_mask(image, resampled_mask)

                # Append to mask 
                mask_rois.append(masked_data.mean(axis = 1))

            # Calculate ROI average
            mask_rois = np.vstack(mask_rois)
            subject_roi = np.nanmean(mask_rois, axis = 0)

            # Calculate subjects standard deviation from ROI
            subject_std = (subject_roi - roi_avg[:len(subject_roi)]) /roi_std[:len(subject_roi)]

            # Check if subject directory exists
            if not os.path.exists(f"{deviation_dir}{subject_dir}/ses-0/"):
                os.makedirs(f"{deviation_dir}{subject_dir}/ses-0/")

            # Save subject deviation
            np.save(roi_dev_filename, subject_std)
            print(f"Saved {roi_dev_filename}")