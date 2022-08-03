#!/bin/bash

# usage: mask_copes.sh <path/to/first_level.feat/stats/>

# get path of cope1.nii.gz
cope="$1"cope1.nii.gz

# get path of mask
mask=$(dirname $(dirname $1))/$(ls $(dirname $(dirname $1)) | grep mask.nii.gz)

# multiply cope by mask and save to new file with cope
fslmaths $cope -mas $mask "${cope%%.*}"_mask."${cope#*.}"
