#!/bin/bash

patid=$1

mkdir -p $cifti_masks_dir
cp $fs_segmentation_dir/$patid/mri/wmparc.mgz $cifti_masks_dir

pushd $cifti_masks_dir
cp $cifti_masks_label_templates_dir/FreeSurferSubcorticalLabelTableLut* $cifti_masks_dir
cp $cifti_masks_label_templates_dir/*.atlasroi.32k_fs_LR.shape.gii $cifti_masks_dir
mri_convert -rl $fs_segmentation_dir/$patid/mri/rawavg.mgz wmparc.mgz wmparc.nii
niftigz_4dfp -4 wmparc.nii wmparc
t4img_4dfp none wmparc wmparc_333_new -O333 -n
niftigz_4dfp -n wmparc_333_new wmparc_333_new
$workbenchdir/wb_command -volume-label-import wmparc_333_new.nii.gz FreeSurferSubcorticalLabelTableLut_nobrainstem_LR.txt subcortical_mask_LR_333_new.nii -discard-others -unlabeled-value 0
$workbenchdir/wb_command -volume-label-import wmparc_333_new.nii.gz FreeSurferSubcorticalLabelTableLut_nobrainstem_sub_L_cbll_R.txt subcortical_mask_sub_L_cbll_R_new.nii -discard-others -unlabeled-value 0
$workbenchdir/wb_command -volume-label-import wmparc_333_new.nii.gz FreeSurferSubcorticalLabelTableLut_nobrainstem_sub_R_cbll_L.txt subcortical_mask_sub_R_cbll_L_new.nii -discard-others -unlabeled-value 0
rm wmparc.mgz
popd
