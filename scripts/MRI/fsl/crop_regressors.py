# usage: python3 crop_regressors.py /path/to/BIDS/dataset/fmriprepfolder

from glob import glob
import sys
from tqdm import tqdm
from os.path import join

bids_path = sys.argv[1]
if "derivatives/fmriprep" not in bids_path:
    bids_path = join(bids_path, "derivatives/fmriprep")

fs = glob(bids_path+"**/*regressors.txt", recursive=True)

for fpath in tqdm(fs):
    if len(glob(fpath.split('.')[0]+"*crop*.txt")) == 0:
        fr = open(fpath, 'r')
        lines = len(fr.readlines())
        fr.close()
        fr = open(fpath, 'r')

        fw = open(fpath.split('.')[0]+"_crop.txt", 'w')

        for i, line in enumerate(fr.readlines()):
            if (i != 0) and (i != lines-1):
                fw.write(line)
        fr.close()
        fw.close()
