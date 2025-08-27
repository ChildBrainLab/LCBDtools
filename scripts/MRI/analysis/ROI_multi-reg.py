import sys, os, random, nilearn, csv, scipy
from glob import glob
import nibabel as nib
from sklearn.linear_model import LinearRegression
from nilearn import datasets
from nilearn.image import math_img, load_img, resample_to_img
from nilearn.plotting import plot_roi
from nilearn.masking import apply_mask
from scipy.stats import zscore
import numpy as np
import pandas as pd
import statsmodels.api as sm

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
    'A': 1604,
    'B': 1704,
    'C': 1653
}

movie_segments = {
    'A': [ind for ind in range(0, 1605, 100)] + [1604],
    'B': [ind for ind in range(0, 1705, 100)] + [1704],
    'C': [ind for ind in range(0, 1653, 100)] + [1653]
}

high_conflict = [5000, 5025,5026,5027,5029,5033,5034,5034,5035,5036,5038,
5039,5040,5043,5044,5046,5049,5051,5051,5057,5062,5075,5075,5091,5093,
5097,5098,5100,5104,5105,5105,5110,5117,5118,5119,5121,5121,5122,5123,
5125,5126,5126,5126,5127,5128,5133,5136,5139,5140,5141,5142,5142,5143,
5144,5146,5147,5148,5149,5150,5151,5153,5159,5160,5163,5170,5170,5171,
5174,5175,5177,5178,5180,5184,5186,5188,5190,5191,5193,5194,5195,5198,
5200,5200,5203,5204,5207,5210,5212,5214,5215,5216,5223,5225,5225,5227,
5228,5231,5233,5235,5236,5241,5243,5243,5245,5246,5247,5249,5250,5252,
5255,5256]
high_conflict = set([str(sub) for sub in high_conflict])

low_conflict = [5002,5003,5003,5007,5008,5009,5009,5010,5011,5012,5013,
5015,5017,5018,5019,5020,5021,5022,5023,5024,5028,5030,5032,5032,5037,
5042,5042,5045,5048,5050,5050,5050,5052,5053,5053,5055,5055,5058,5059,
5059,5060,5060,5061,5063,5064,5069,5070,5071,5072,5073,5074,5074,5076,
5077,5078,5080,5080,5081,5083,5083,5084,5085,5086,5087,5089,5092,5094,
5094,5096,5096,5099,5099,5101,5102,5108,5108,5109,5112,5113,5113,5114,
5116,5120,5124,5130,5134,5137,5138,5138,5152,5157,5162,5165,5165,5166,
5166,5169,5173,5179,5183,5185,5189,5192,5197,5201,5218,5219,5219,5222,
5222,5229,5229,5230,5232,5237,5244,5251,5251]
high_conflict = set([str(sub) for sub in low_conflict])

# Grab movie valence, volatility, loudness and luminance regressors
movie_valence = {'A': None, 'B': None, 'C': None}
movie_volatilities = {'A': None, 'B': None, 'C': None}
movie_luminance = {'A': None, 'B': None, 'C': None}
movie_loudness = {'A': None, 'B': None, 'C': None}
for movie in ['A', 'B', 'C']:
    # Grab movie valence
    with open(f'/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/AHKJ_rating_avg_movie{movie}.txt', 'r') as file:
        content = file.readlines()
    content = [float(line.split('\n')[0]) for line in content]
    movie_valence[movie] = content

    # Grab movie valence volatility
    with open(f'/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/MRI/analysis/AHKJ_movie{movie}_volatility.txt', 'r') as file:
        content = file.readlines()
    content = [float(line.split('\n')[0]) for line in content]
    movie_volatilities[movie] = content

    # Grab movie loudness
    with open(f'/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/AHKJ_loudness_movie{movie}.txt', 'r') as file:
        content = file.readlines()
    content = [float(line.split('\n')[0]) for line in content]
    movie_loudness[movie] = content

    # Grab movie luminance
    with open(f'/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/AHKJ_luminance_movie{movie}.txt', 'r') as file:
        content = file.readlines()
    content = [float(line.split('\n')[0]) for line in content]
    movie_luminance[movie] = content

session = '0'

# Define variable to store subject-ROI correlations
csv_contents = []

print(f"ROIs")
for key, value in ROIs.items():
    print(f"{key}: {value}")

_overwrite = True
# Iterate through movies
for movie, movie_length in movies.items(): # For each movie

    roi_list = list(ROIs.keys())
    random.shuffle(roi_list)

    # Grab subject pool that saw this movie
    subject_files = glob(f"{input_dir}sub-*/ses-{session}/func/sub-*_ses-0_task-movie{movie}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_7mm_smoothed.nii") # Grab all subjects for movie
    subjects = [subject.split('/')[-4].split('sub-')[-1] for subject in subject_files] # Grab the subject ID from the file path
    subjects = [subject for subject in subjects if subject[-5:] != '_copy'] # Remove empty strings

    # Grab all subject files and shuffle
    subject_files = glob(f"{input_dir}sub-*/ses-0/func/sub-*_ses-0_task-movie{movie}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold_7mm_smoothed.nii") # Grab all subjects for movie

    for roi in roi_list: # Iterate through ROIs
        print(f"movie{movie}-{roi}") # Construct ROI name
        roi_name = '-'.join(roi.split(' '))

        for subject_file in subject_files:
            
            # Grab subject directory
            subject_dir = subject_file.split('/')[-4]
            subject = subject_dir[-5:]

            print(f"Regressing on {subject} {roi} movie {movie}")

            # Skip if the folder is a copy
            if subject == '_copy':
                print("Skipping copy")
                continue
            
            # Load the ROI average and standard deviation for the subject
            if os.path.exists(f"{output_dir}{subject}/movie{movie}_{roi_name}_group_median_timecourse.npy") == False:
                continue
            roi_avg = np.load(f"{output_dir}{subject}/movie{movie}_{roi_name}_group_median_timecourse.npy")
            roi_std = np.load(f"{output_dir}{subject}/movie{movie}_{roi_name}_group_std_timecourse.npy")

            masks = ROIs[roi]['masks'] # Grab the ROI mask

            # Load their data
            image = nib.load(subject_file)

            mask_rois = []
            for mask in masks:# Iterate through masks
                print(f"Calculating {subject_file} correspondend from ROI {roi_name}...")

                # Resample mask to the subjects space
                resampled_mask = nilearn.image.resample_to_img(mask, image, interpolation = 'nearest')

                # Apply mask to get (n_timepoints x n_voxels)
                masked_data = nilearn.masking.apply_mask(image, resampled_mask)

                print(f"{subject_file} - {roi} - masked shape: {masked_data.shape}, nanmean: {np.nanmean(masked_data)}")

                # Append to mask - use median to instead of mean to remove outliers like CSF and motion
                mask_rois.append(np.nanmean(masked_data, axis=1))

            # Calculate ROI average
            mask_rois = np.vstack(mask_rois)
            subject_roi = np.nanmean(mask_rois, axis = 0)
            
            # Calculate subject difference from group
            subject_difference = roi_avg[:len(subject_roi)] - subject_roi
            print(f"{subject}: diff mean = {np.mean(subject_difference)}, std = {np.std(subject_difference)}")
            
            for segment_ind, segment_start in enumerate(movie_segments[movie][:-1]):
                # Check if the segment is out of index
                if segment_start > len(subject_difference):
                    break
                
                # Grab segment end
                segment_end = movie_segments[movie][segment_ind + 1]

                # Grab group movie segment
                if segment_start < subject_roi.shape[0]:
                    if segment_end > subject_roi.shape[0]:
                        short_roi_mean = roi_avg[segment_start:subject_roi.shape[0]]
                    else:
                        short_roi_mean = roi_avg[segment_start:segment_end]

                # Shorten segment if subject_difference is smaller
                if segment_end > len(subject_difference):
                    segment_end = len(subject_difference)
                    

                # Run multiple regression
                data = {
                    "X1": movie_valence[movie][segment_start:segment_end],
                    "X2": movie_volatilities[movie][segment_start:segment_end],
                    "X3": movie_loudness[movie][segment_start:segment_end],
                    "X4": movie_luminance[movie][segment_start:segment_end],
                    "Y":  subject_difference[segment_start:segment_end]
                }
                for key, value in data.items():
                    print(f"{key} mean: {np.nanmean(value)}")
                    print(f"{value}")

                # Add data to a df  
                df = None
                df = pd.DataFrame(data)

                # Independent variables, including noise
                X_variables = None
                X_variables = df[["X1", "X2", "X3", "X4"]]
                X = sm.add_constant(X_variables)
                Y = df["Y"]

                # Fit regression
                model = None
                model = sm.OLS(Y, X).fit()
                
                # Grab results
                beta_valence = model.params["X1"]
                intercept = model.params["const"]

                # Calculate segment mean valence
                valence_mean = np.nanmean(movie_valence[movie][segment_start:segment_end])

                # Calculate segment mean volatility
                volatility_mean = np.nanmean(movie_volatilities[movie][segment_start:segment_end])

                # Grab subject trait
                conflict = 'High'
                if int(subject[:4]) in high_conflict:
                    conflict = 'High'
                if int(subject[:4]) in low_conflict:
                    conflict = 'Low'

                # Append multiple regression results for subject segment
                csv_contents.append([subject, movie, roi, f'{segment_start}-{segment_end}', conflict, valence_mean, volatility_mean, beta_valence, intercept])

header = ['Subject', 'Movie', 'ROI', 'Segment', 'Conflict Group', 'Segment Average Valence', 'Segment Average Volatility', 'Emotional Valence Beta', 'Intercept']
with open(f"{deviation_dir}subject-ROI_multiple_regression.csv", 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(csv_contents)
