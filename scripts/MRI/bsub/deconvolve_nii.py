import os
import nibabel as nib
from glob import glob
import numpy as np
from scipy.stats import gamma
from scipy.signal import fftconvolve


def deconvolve_hrf(image):

    def generate_hrf(TR, length=30, peak=6, undershoot=16, ratio=6, delay=0):
        timepoints = np.arange(0, length, TR)
        peak_response = gamma.pdf(timepoints, peak) 
        undershoot_response = gamma.pdf(timepoints, undershoot) / ratio
        hrf = peak_response - undershoot_response
        hrf = hrf / np.max(hrf)  # Normalize the HRF
        return hrf

    # Example: Generate HRF for TR=2s
    hrf = generate_hrf(0.8)

    def wiener_deconvolution(signal, hrf, noise_level=0.01):
        H = np.fft.fft(hrf, n=len(signal))
        S = np.fft.fft(signal)
        H_conj = np.conj(H) 
        G = H_conj / (H * H_conj + noise_level)
        deconvolved = np.real(np.fft.ifft(S * G))
        return deconvolved

    # Apply deconvolution voxel-wise
    deconvolved_data = np.zeros_like(image)
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            for z in range(image.shape[2]):
                time_series = image[x, y, z, :]
                if np.any(time_series):  # Check for non-empty signal
                    deconvolved_data[x, y, z, :] = wiener_deconvolution(time_series, hrf)
    return deconvolved_data

nii_files = glob("/storage1/fs1/perlmansusan/Active/moochie/analysis/CARE/fMRI_data/derivatives/fmriprep/sub-*/ses-*/func/*ses-0*movie*MNIPediatricAsym*preproc_bold_6mm_smoothed.nii")

files = '\n'.join(nii_files)
print(f"Files found...\n{files}")

for nii_file in nii_files:
    new_name = nii_file.split(".nii")[0] + "_deconvolved.nii"

    if os.path.exists(new_name):
        print(f"{new_name} file exists, skipping...")
        continue

    image_file = nib.load(nii_file)

    image = image_file.get_fdata()

    print(f"Deconvolving {nii_file}...")
    deconvolved_data = deconvolve_hrf(image)

    deconvolved_image = nib.Nifti1Image(deconvolved_data, image_file.affine, image_file.header)

    nib.save(deconvolved_image, new_name)



    

