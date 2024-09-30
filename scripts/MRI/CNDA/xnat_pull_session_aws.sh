#!/bin/bash

# usage: bash xnat_pull_session.sh <session number>

export XNAT_HOST=https://cnda.wustl.edu

Xnatdownload\
	--host https://cnda.wustl.edu\
	--project NP1166\
	--directory CNDA_downloads\
	--sess $1\
	--scantype "T1 MPRAGE Cor,dMRI_dir98_AP_SBRef,dMRI_dir98_AP,dMRI_dir98_PA_SBRef,dir98_PA,movie_fmap_1,movie_fmap_2,movie_versionA_PA_SBRef,movie_versionA_PA,movie_versionB_PA_SBRef,movie_versionB_PA,movie_versionC_PA_SBRef,movie_versionC_PA"\
	--quality usable\
	--rs DICOM\

grep -qxF $1 .CNDA_downloads/NP1166/CNDA_downloaded.txt || echo $1 >> .CNDA_downloads/NP1166/CNDA_downloaded.txt
