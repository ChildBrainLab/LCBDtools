import numpy as np
from nilearn.datasets import load_mni152_template
from nilearn.image import new_img_like
from nilearn.plotting import plot_roi
from nilearn.image.resampling import coord_transform

# PVN based on Zhang et al., 2017

# Load MNI 2mm template
template_img = load_mni152_template(resolution=2)
template_affine = template_img.affine
template_shape = template_img.shape

# PVN coordinate (centered in midline hypothalamus)
pvn_coord_mni = (0, -1, -8)
radius_mm = 2  # smaller due to tiny structure

# Create empty volume
pvn_data = np.zeros(template_shape, dtype=np.uint8)

# Convert MNI → voxel
voxel_coords = np.round(coord_transform(*pvn_coord_mni, np.linalg.inv(template_affine))).astype(int)

# Create spherical mask around PVN
for x in range(-radius_mm, radius_mm + 1):
    for y in range(-radius_mm, radius_mm + 1):
        for z in range(-radius_mm, radius_mm + 1):
            if x**2 + y**2 + z**2 <= radius_mm**2:
                i, j, k = voxel_coords + np.array([x, y, z])
                if 0 <= i < template_shape[0] and 0 <= j < template_shape[1] and 0 <= k < template_shape[2]:
                    pvn_data[i, j, k] = 1

# Create mask image
pvn_mask_img = new_img_like(template_img, pvn_data)
pvn_mask_img.to_filename("custom_pvn_mask.nii.gz")
