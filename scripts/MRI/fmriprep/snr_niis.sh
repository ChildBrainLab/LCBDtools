#!/bin/bash

# usage: snr_niis.sh <path/to/nii.gz>

# get mean image across time
fslmaths $1 -Tmean "${1%%.*}"_Tmean."${1#*.}"

# get std image across time
fslmaths $1 -Tstd "${1%%.*}"_Tstd."${1#*.}"

# get SNR (mean / std)
fslmaths "${1%%.*}"_Tmean."${1#*.}" -div "${1%%.*}"_Tstd."${1#*.}" "${1%%.*}"_SNR."${1#*.}"
