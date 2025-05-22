import numpy as np
from nilearn.datasets import load_mni152_template
from nilearn.image import new_img_like
from nilearn.plotting import plot_roi
import nibabel as nib

# BNST mask based on Avery et al., 2014

# Load MNI 2mm template
template_img = load_mni152_template(resolution=2)
template_affine = template_img.affine
template_shape = template_img.shape

# BNST coordinates in MNI space (L and R)
bnst_coords_mni = [(-6, 2, 0), (6, 2, 0)]
radius_mm = 3  # Radius in mm

# Create empty volume
bnst_data = np.zeros(template_shape, dtype=np.uint8)

# Helper: MNI → voxel coords
from nilearn.image.resampling import coord_transform

for coord in bnst_coords_mni:
    # Convert to voxel space
    voxel_coords = np.round(coord_transform(*coord, np.linalg.inv(template_affine))).astype(int)

    # Create a sphere
    for x in range(-radius_mm, radius_mm + 1):
        for y in range(-radius_mm, radius_mm + 1):
            for z in range(-radius_mm, radius_mm + 1):
                if x**2 + y**2 + z**2 <= radius_mm**2:
                    i, j, k = voxel_coords + np.array([x, y, z])
                    if 0 <= i < template_shape[0] and 0 <= j < template_shape[1] and 0 <= k < template_shape[2]:
                        bnst_data[i, j, k] = 1

# Create and save new mask
bnst_mask_img = new_img_like(template_img, bnst_data)
bnst_mask_img.to_filename("custom_bnst_mask.nii.gz")
