import sys, os, random, nilearn, scipy, csv
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
ROI_temp = {'masks': [], 'subject deviation': {},}

ROIs = { # Define regions of interest (ROI)
    'bed nucleus of the stria terminalis': {'masks': [], 'subject deviation': {},},
    'paraventricular nucleus': {'masks': [], 'subject deviation': {},},
    'dorsomedial prefrontal': {'masks': [], 'subject deviation': {},},
    'temporoparietal junction': {'masks': [], 'subject deviation': {},},
    'ventromedial prefrontal': {'masks': [], 'subject deviation': {},},
    'orbitofrontal_cortex': {'masks': [], 'subject deviation': {},},
    'ventrolateral prefrontal': {'masks': [], 'subject deviation': {},},
    'anterior cingulate': {'masks': [], 'subject deviation': {},},
    'anterior insula': {'masks': [], 'subject deviation': {},},
    'amygdala': {'masks': [], 'subject deviation': {},},
    'hippocampus': {'masks': [], 'subject deviation': {},}
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
    'A': 1605,
    'B': 1705,
    'C': 1653
}

session = '0'

overwrite = True


# Define variable to store subject-subject correlations
csv_r_contents = []
csv_p_contents = []

# Iterate through movies
for movie in movies.keys(): # For each movie
    # Grab subject pool that saw this movie
    subject_files = glob(f"{input_dir}sub-*/ses-{session}/func/sub-*_ses-0_task-movie{movie}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_7mm_smoothed.nii") # Grab all subjects for movie
    subjects = [subject.split('/')[-4].split('sub-')[-1] for subject in subject_files] # Grab the subject ID from the file path
    subjects = [subject for subject in subjects if subject[-5:] != '_copy'] # Remove empty strings

    sub_dev_corr = {roi : {} for roi in ROIs.keys()} # Store subject-subject correlations for each ROI
    dev_corr_matrix = np.zeros((len(ROIs.keys()), len(subjects), len(subjects), 2)) # Store subject-subject correlations for each ROI
    

    for roi_ind, roi in enumerate(ROIs.keys()): # Iterate through ROIs
        print(f"Correlating subjects for movie {movie}-{roi}")
        roi_name = '-'.join(roi.split(' '))

        # Permute through all subject combos
        for first_ind, first_subject in enumerate(subjects):
            if first_subject not in sub_dev_corr[roi].keys():
                sub_dev_corr[roi][first_subject] = {}

            # Grab subject deviation
            first_dev_file = f"{deviation_dir}sub-{first_subject}/ses-{session}/sub-{first_subject}_ses-{session}_roi-{roi_name}_deviation.npy"

            first_dev = np.load(first_dev_file) # Load their deviation

            for second_ind, second_subject in enumerate(subjects):
                if second_subject not in sub_dev_corr[roi][first_subject].keys():
                    sub_dev_corr[roi][first_subject][second_subject] = {}

                if first_subject == second_subject: # Skip if same subject
                    dev_corr_matrix[roi_ind, first_ind, second_ind, 0] = np.nan
                    dev_corr_matrix[roi_ind, first_ind, second_ind, 1] = np.nan
                    sub_dev_corr[roi][first_subject][second_subject] = (np.nan, np.nan)
                    continue

                second_dev_file = f"{deviation_dir}sub-{second_subject}/ses-{session}/sub-{second_subject}_ses-{session}_roi-{roi_name}_deviation.npy"
            
                second_dev = np.load(second_dev_file) # Load their deviation

                shortest_len = min(len(first_dev), len(second_dev)) # Grab the shortest length
                first_dev = first_dev[:shortest_len] # Trim the first subject
                second_dev = second_dev[:shortest_len] # Trim the second subject
                
                results = scipy.stats.spearmanr(first_dev, second_dev) # Correlate first subject with second subject
                r_value = results.statistic # Grab r value
                p_value = results.pvalue # Grab p value
                print(f"{first_subject} vs {second_subject}: {r_value} ({p_value})")

                # store r value
                sub_dev_corr[roi][first_subject][second_subject] = (r_value, p_value)
                dev_corr_matrix[roi_ind, first_ind, second_ind, 0] = r_value
                dev_corr_matrix[roi_ind, first_ind, second_ind, 1] = p_value

    # Save the subject-subject correlation for this movie
    np.save(f"{deviation_dir}movie{movie}_subject-subject_correlation.npy", dev_corr_matrix)

    # Save csv of subject-subject correlation for this movie
    for roi_ind, roi in enumerate(ROIs.keys()): # Iterate through ROIs
        for first_ind, first_subject in enumerate(subjects):
            for second_ind, second_subject in enumerate(subjects):
                csv_r_contents.append([first_subject, second_subject, movie] + [sub_dev_corr[roi][first_subject][second_subject][0] for roi in ROIs.keys()])
                csv_p_contents.append([first_subject, second_subject, movie] + [sub_dev_corr[roi][first_subject][second_subject][1] for roi in ROIs.keys()])

header = ['First Subject', 'Second Subject', 'Movie'] + [roi for roi in ROIs.keys()]
with open(f"{deviation_dir}subject-subject_correlation.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(csv_r_contents)

header = ['First Subject', 'Second Subject', 'Movie'] + [roi for roi in ROIs.keys()]
with open(f"{deviation_dir}subject-subject_correlation_p-values.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(csv_p_contents)

# For each movie

    # For each ROI

        # For each subject

            # Grab subject ROI

            # For each subject to compare against (all)

                # Grab second subjects deviation

                # Correlate first subject with second subject

                # Store r value
        
    # Store 3D array for each movie (i.e. ROI x subject x subject)
    # or store 2D array for each movie-ROI combo (subject x subject)?


