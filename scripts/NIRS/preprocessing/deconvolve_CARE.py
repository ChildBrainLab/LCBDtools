import os, random, mne
import hrfunc as hrf
from glob import glob

scan_filenames = glob("/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/NIRS_data_clean_2/*/V0/*/")

random.shuffle(scan_filenames)

montage = hrf.load_montage("/storage1/fs1/perlmansusan/Active/moochie/github/LCBDtools/scripts/NIRS/hrfunc/P-CAT_hrfs_new.json")

for scan_filename in scan_filenames:
    split = scan_filename.split('/')
    basename = split[-2]
    directory = "/".join(split)

    new_filename = f"deconvolved_{basename}.fif"
    
    # check if it's a parent
    print(basename)
    print(directory)
    if basename[4] == "_":
        continue

    if os.path.exists(f"{directory}/{new_filename}"):
        print(f"Skipping {new_filename}, already deconvolved...")
        continue

    print(f"Estimating neural activity in {scan_filename}")
    scan = mne.io.read_raw_nirx(scan_filename)

    montage.estimate_activity(scan)

    
    scan.save(f"{directory}/{new_filename}")
    print(f"Saved {new_filename}")