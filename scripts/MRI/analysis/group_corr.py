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
    'bed nucleus of the stria terminalis': [[], [], []],
    'paraventricular nucleus': [[], [], []],
    'dorsomedial prefrontal': [[], [], []],
    'temporoparietal junction': [[], [], []],
    'ventromedial prefrontal': [[], [], []],
    'orbitofrontal_cortex': [[], [], []],
    'ventrolateral prefrontal': [[], [], []],
    'anterior cingulate': [[], [], []],
    'anterior insula': [[], [], []],
    'amygdala': [[], [], []],
    'hippocampus': [[], [], []]
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

# Load the subject correlation matrix
corr_filename = f"{deviation_dir}subject-subject_correlation.csv"
with open(corr_filename, 'r') as csvfile:
    reader = csv.reader(csvfile)
    # Skip the header
    header = next(reader)

    # Read the correlation matrix
    corr_matrix = []
    for row in reader:
        corr_matrix.append(row)

    # Convert to numpy array
    corr_matrix = np.array(corr_matrix)

# Load the subject correlation matrix
p_corr_filename = f"{deviation_dir}subject-subject_correlation_p-values.csv"
with open(p_corr_filename, 'r') as csvfile:
    reader = csv.reader(csvfile)
    # Skip the header
    header = next(reader)

    # Read the correlation matrix
    corr_p_matrix = []
    for row in reader:
        corr_p_matrix.append(row)

    # Convert to numpy array
    corr_p_matrix = np.array(corr_p_matrix)

# Define a p value significance threshold
significance_value = 0.001
for roi_ind, roi_name in zip(range(3, 14), ROIs.keys()):

    for row_ind in range(1, corr_matrix.shape[0]):
        # Get the subject ID
        first_subject = str(corr_matrix[row_ind, 0])
        second_subject = str(corr_matrix[row_ind, 1])
        corr_value = float(corr_matrix[row_ind, roi_ind])
        p_value = float(corr_matrix[row_ind, roi_ind])

        if p_value > significance_value:
            continue

        # Check if the subjects are in high_conflict group
        if str(first_subject[:-1]) in high_conflict:
            first_subject = 'high_conflict'
        else:
            first_subject = 'low_conflict'
        if str(second_subject[:-1]) in high_conflict:
            second_subject = 'high_conflict'
        else:
            second_subject = 'low_conflict'
        
        if first_subject == second_subject:
            if first_subject == 'high_conflict':
                ROIs[roi_name][2].append(corr_value)
            else:
                ROIs[roi_name][1].append(corr_value)
        else:
            ROIs[roi_name][0].append(corr_value)
# Calculate group level correlation
rows = []
for roi_name in ROIs.keys():
    roi_data = ROIs[roi_name]
    high_conflict_corr = np.nanmean(roi_data[2])
    low_conflict_corr = np.nanmean(roi_data[1])
    diff_conflict_corr = np.nanmean(roi_data[0])
    rows.append([roi_name, high_conflict_corr, low_conflict_corr, diff_conflict_corr])

# Save the group level correlation
output_filename = f"{deviation_dir}/group_ROI_correlations.csv"
with open(output_filename, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['ROI', 'High Conflict', 'Low Conflict', 'Different Conflict'])
    writer.writerows(rows)