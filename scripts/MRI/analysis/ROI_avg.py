import sys, os, copy, random
from glob import glob
import nibabel as nib
from nilearn import datasets
from nilearn.image import math_img, load_img, resample_to_img
from nilearn.plotting import plot_roi
from nilearn.masking import apply_mask
import numpy as np

# Define runtime variables defining where data is and where to output results
output_dir = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/ROI_averages/'
input_dir = '/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/MRI_data/derivatives/fmriprep/'

# Region of interest structure for storing intermediary data
ROI_temp = {'masks': [], 'average_timecourse': [], 'subjects': []}

ROIs = { # Define regions of interest (ROI)
    'bed nucleus of the stria terminalis': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'paraventricular nucleus': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'dorsomedial prefrontal': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'temporoparietal junction': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'ventromedial prefrontal': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'orbitofrontal_cortex': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'ventrolateral prefrontal': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'anterior cingulate': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'anterior insula': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'amygdala': {'masks': [], 'average_timecourse': [], 'subjects': []},
    'hippocampus': {'masks': [], 'average_timecourse': [], 'subjects': []}
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

# Load custom BNST (Avery et al., 2014) and PVN (Zhang et al., 2017) masks
ROIs['bed nucleus of the stria terminalis']['masks'].append(nib.load('/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/analysis/custom_bnst_mask.nii'))
ROIs['paraventricular nucleus']['masks'].append(nib.load('/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/analysis/custom_pvn_mask.nii'))

# Define movies being analyzed
movies = {
    'C': 1653,
    'A': 1605,
    'B': 1705
}

_overwrite = False

print(f"ROIs {ROIs.items()}")

movie_names = list(movies.keys())
print(movie_names)
random.shuffle(movie_names)
for movie_name in reversed(movie_names): # For each movie
    movie = movies[movie_name] # Get movie number
    movie_rois = copy.deepcopy(ROIs) # Create a copy of the ROI

    roi_names = list(ROIs.keys())
    random.shuffle(roi_names)
    for roi in roi_names: # Iterate through ROIs
        print(f"Calculating {roi} average for movie {movie_name}")

        masks = ROIs[roi]['masks'] # Grab roi mask
        print(f"Masks: {masks}")

        file_identifier = f"{input_dir}sub-*/ses-0/func/*ses-0*MNIP*6mm_smoothed.nii"
        files = glob(file_identifier) # Grab all subjects for movie
        random.shuffle(files)

        print(f"Files found {len(files)}\n{"\n -".join(files)}")
        for soi_file in files: # For each subjects data
            # Grab subject ID
            subject = soi_file.split('/')[-1].split('_')[0].split('-')[1]

            ROI_mask_medians = [] # Create variable for storing intermediary values
            max_len = 0

            # Skip if average already calculated
            if os.path.exists(f"{output_dir}{subject}/movie{movie_name}_{'-'.join(roi.split(' '))}_group_median_timecourse.npy") and _overwrite == False:
                print(f'File already exists: {f"{output_dir}{subject}/movie{movie_name}_{'-'.join(roi.split(' '))}_group_median_timecourse.npy"}')
                continue
            elif os.path.exists(f"{output_dir}{subject}/movie{movie_name}_{'-'.join(roi.split(' '))}_group_median_timecourse.npy") and _overwrite == True:
                os.remove(f"{output_dir}{subject}/movie{movie_name}_{'-'.join(roi.split(' '))}_group_median_timecourse.npy")
                os.remove(f"{output_dir}{subject}/movie{movie_name}_{'-'.join(roi.split(' '))}_group_std_timecourse.npy")

            for subject_file in files:
                if soi_file == subject_file:
                    print(f"Skipping subject {subject} from their group mean calculation...")
                    continue

                if "run_1" in subject_file or "run_01" in subject_file:
                    print(f"Skipping first runm scan {subject_file}") 
                    continue

                if "_copy" in subject_file:
                    print(f"Skipping {subject_file} since it's a copy...")
                    continue

                print(f"Calculating average for {subject_file}")
                image = nib.load(subject_file) # Load their data
                
                length = image.shape[3] # Grab image shape
                if length > max_len: # Record if new max length found
                    max_len = length

                for mask in masks:# Iterate through masks
                    # Resample mask to the subjects space
                    resampled_mask = resample_to_img(mask, image, interpolation='nearest')

                    # Apply mask to get (n_timepoints x n_voxels)
                    masked_data = apply_mask(image, resampled_mask)

                    # Average across voxels -> (n_timepoints,)
                    mask_median_timecourse = np.median(masked_data, axis=1)
                    print(mask_median_timecourse)

                    ROI_mask_medians.append(mask_median_timecourse)

            # Pad the ROI
            for mask_ind, mask_median in enumerate(ROI_mask_medians):
                new_median = np.concatenate([mask_median, np.array([np.nan for _ in range(len(mask_median), max_len)])])
                ROI_mask_medians[mask_ind] = new_median

            # Stack mask averages and calculate average ROI average
            mask_median_timecourses = np.vstack(ROI_mask_medians)
            ROI_median_timecourse = np.nanmean(mask_median_timecourses, axis = 0)
            ROI_std_timecourse = np.nanstd(mask_median_timecourses, axis = 0)

            # Check if participant has a folder
            if os.path.exists(f"{output_dir}{subject}") is False:
                os.mkdir(f"{output_dir}{subject}")

            # Save the average for the ROI
            np.save(f"{output_dir}{subject}/movie{movie_name}_{'-'.join(roi.split(' '))}_group_median_timecourse.npy", ROI_median_timecourse)
            np.save(f"{output_dir}{subject}/movie{movie_name}_{'-'.join(roi.split(' '))}_group_std_timecourse.npy", ROI_std_timecourse)



