import os
from glob import glob
from tqdm import tqdm
import sys

# usage: python get_feat_dirs.py /path/to/BIDS/dir

bidsdir = sys.argv[1]

f = open("/home/{}/cope_subs.txt".format(os.environ.get("USER")), 'w')

# /scratch/claytons/MRI_data_clean/derivatives/fmriprep/sub-51271/ses-0/func/first_level.feat
feats = glob(bidsdir+"derivatives/fmriprep/sub*/**/first_level.feat", recursive=True)

for feat in feats:
    # print(feat)
    if "ses-0" in feat:
        cope = feat + "/stats/cope1.nii.gz"
        if os.path.exists(cope):
            f.write(cope)
            f.write("\n")
        else:
            continue
    else:
        continue
