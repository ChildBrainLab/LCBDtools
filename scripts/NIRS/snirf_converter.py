from glob import glob
import mne_nirs, mne, os


nirx_directories = glob("/storage1/fs1/perlmansusan/Active/moochie/study_data/P-CAT/R56/restructured_data/fnirs_data/*/*/*/")

# Load the NIRx data directory (path should contain all files: .wl1, .wl2, .hdr, etc.)
for nirx_dir in nirx_directories:
    snirf_filename = nirx_dir.split('/')[-2] + '.snirf'
    if os.path.exists(f"{nirx_dir}{snirf_filename}") == False:
        try:
            print(f"Converting {nirx_dir} to snirf...")
            raw = mne.io.read_raw_nirx(nirx_dir, preload=True)
            mne_nirs.io.write_raw_snirf(raw, f"{nirx_dir}{snirf_filename}", True)
            print(f"SNIRF file saved as {snirf_filename}...")
        except:
            print(f"Failed to export {snirf_filename}...")
    else:
        print(f"{snirf_filename} exists, skipping...")
