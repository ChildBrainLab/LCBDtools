import os
import shutil
from glob import glob
from tqdm import tqdm
import sys

# usage: python fix_feat_reg.py /path/to/bids/dir

bidsdir = sys.argv[1]

fpdir = os.path.join(bidsdir, "derivatives/fmriprep")

feat_dirs = glob(fpdir + "/sub*/ses-0/func/first_level.feat", recursive=True)

for feat in tqdm(feat_dirs):
    try:
        # remove any existing reg dir, then make a new one
        if os.path.exists(feat+"/reg"):
            shutil.rmtree(feat+"/reg")
        os.mkdir(feat+"/reg")

        # copy feat identity matrix to reg dir
        shutil.copy("/export/fsl/fsl-6.0.5/etc/flirtsch/ident.mat", feat+"/reg/example_func2standard.mat")

        # copy the mean func image to the reg folder
        shutil.copy(feat+"/mean_func.nii.gz", feat+"/reg/standard.nii.gz")

    except:
        print("Failure.")
        print("Skipping: ", feat)
        continue
    
