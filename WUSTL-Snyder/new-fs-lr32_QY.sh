#!/bin/sh

#GW edits
#Sept2012
#QY edits directories for AttnAnxiety study wave1
#MM edits to make more general, allow passing in a file that defines all project-specific directories

#-------------------------------------Define Study Parameter ---------------------------------------------#

Subject=$1
StudyFolder=$preproc_dir/$Subject

InputAtlasName="TRIO_KY_NDC" #e.g., 7112b, DLBS268, MNI152 (will be used to name folders in subject's folder)
FreesurferImportLocation="$fs_segmentation_dir" #Input freesurfer path
MPRImportLocation="$preproc_dir/$Subject/atlas" #Input MPR path (atlas directory from avi scripts or wherever the FS input MPR nii is)

FreeSurferInput=${Subject}_mpr_n1_111_t88 #Make sure to rename FreeSurfer input T1w to this name or change throughout to String of your choice (note whether it has .nii.gz or not and keep it that way) 
T1wRestoreImage=${Subject}_mpr_n1_111_t88 # you will change these (???)
T2wRestoreImage=${Subject}_mpr_n1_111_t88 # MO suggested same MPR, it's not used in FreeSurfer2CaretConvertAndRegisterNonlinear.sh
AtlasSpaceT1wImage=${Subject}_mpr_n1_111_t88
AtlasSpaceT2wImage=${Subject}_mpr_n1_111_t88

FinalTemplateSpace="$MPRImportLocation/${Subject}_mpr_n1_111_t88" #Reuse FreeSurfer input T1 image that was used in FS.
DownSampleI="32000" #Downsampled mesh (same as HCP)
DownSampleNameI="32"

#-------------------------------------END study Parameters-----------------------------------------------------------#

#Script and Program Locations:	
CaretAtlasFolder="/data/heisenberg/data1/mario/FSAVG2FSLR_SCRIPTS/global/templates/standard_mesh_atlases" #Copied from Git Repo
PipelineScripts="/data/heisenberg/data1/mario/FSAVG2FSLR_SCRIPTS/PostFreeSurfer/scripts" #From Git Repo
PipelineBinaries="/data/heisenberg/data1/mario/FSAVG2FSLR_SCRIPTS/global/binaries" #From Git Repo
GlobalScripts="/data/heisenberg/data1/mario/FSAVG2FSLR_SCRIPTS/global/scripts" #From Git Repo
Caret5_Command="/data/cn/data1/linux/bin/caret_command64" #Location of Caret5 caret_command
Caret7_Command="/data/heisenberg/data1/mario/wb_dir/workbench/bin_rh_linux64/wb_command" #Location of Caret7 wb_command

#Image locations and names:
T1wFolder="$StudyFolder"/"$Subject"/"$InputAtlasName" #Could try replacing "$InputAtlasName" everywhere with String of your choice, e.g. 7112bLinear
AtlasSpaceFolder="$StudyFolder"/"$Subject"/"$InputAtlasName"
NativeFolder="Native"
FreeSurferFolder="$FreesurferImportLocation"/"$Subject" #$StudyFolder"/"$Subject"/"$InputAtlasName"/"$Subject" 

AtlasTransform="$StudyFolder"/"$Subject"/"$InputAtlasName"/zero #Fake warpfield that is identity
InverseAtlasTransform="$StudyFolder"/"$Subject"/"$InputAtlasName"/zero

T1wImageBrainMask="brainmask_fs" #Name of FreeSurfer-based brain mask -- I think this gets created? GW

#Making directories and copying over relevant data (freesurfer output and mpr):
mkdir -p "$StudyFolder"/"$Subject"/"$InputAtlasName"
cp -R "$FreesurferImportLocation"/"$Subject" "$StudyFolder"/"$Subject"/"$InputAtlasName" #Location of the FreeSurfer subject folder
gzip "$MPRImportLocation"/${FreeSurferInput}.nii
cp "$MPRImportLocation"/${FreeSurferInput}.nii.gz "$StudyFolder"/"$Subject"/"$InputAtlasName"/${FreeSurferInput}.nii.gz #Location of the FreeSurfer input T1w (all gz now)

#I think this stuff below is making the 'fake warpfield that is identity above? GW
fslmaths "$StudyFolder"/"$Subject"/"$InputAtlasName"/${FreeSurferInput}.nii.gz -sub "$StudyFolder"/"$Subject"/"$InputAtlasName"/${FreeSurferInput}.nii.gz "$StudyFolder"/"$Subject"/"$InputAtlasName"/zero.nii.gz 
fslmerge -t "$StudyFolder"/"$Subject"/"$InputAtlasName"/zero_.nii.gz "$StudyFolder"/"$Subject"/"$InputAtlasName"/zero.nii.gz "$StudyFolder"/"$Subject"/"$InputAtlasName"/zero.nii.gz "$StudyFolder"/"$Subject"/"$InputAtlasName"/zero.nii.gz
mv -f "$StudyFolder"/"$Subject"/"$InputAtlasName"/zero_.nii.gz "$StudyFolder"/"$Subject"/"$InputAtlasName"/zero.nii.gz

#Run it
"$PipelineScripts"/FreeSurfer2CaretConvertAndRegisterNonlinear.sh "$StudyFolder" "$Subject" "$T1wFolder" "$AtlasSpaceFolder" "$NativeFolder" "$FreeSurferFolder" "$FreeSurferInput" "$FinalTemplateSpace" "$T1wRestoreImage" "$T2wRestoreImage" "$CaretAtlasFolder" "$DownSampleI" "$DownSampleNameI" "$Caret5_Command" "$Caret7_Command" "$AtlasTransform" "$InverseAtlasTransform" "$AtlasSpaceT1wImage" "$AtlasSpaceT2wImage" "$T1wImageBrainMask" "$PipelineScripts" "$GlobalScripts"
#fsl_sub -q long.q "$PipelineScripts"/FreeSurfer2CaretConvertAndRegisterNonlinear.sh "$StudyFolder" "$Subject" "$T1wFolder" "$AtlasSpaceFolder" "$NativeFolder" "$FreeSurferFolder" "$FreeSurferInput" "$FinalTemplateSpace" "$T1wRestoreImage" "$T2wRestoreImage" "$CaretAtlasFolder" "$DownSampleI" "$DownSampleNameI" "$Caret5_Command" "$Caret7_Command" "$AtlasTransform" "$InverseAtlasTransform" "$AtlasSpaceT1wImage" "$AtlasSpaceT2wImage" "$T1wImageBrainMask" "$PipelineScripts" "$GlobalScripts" #GW:  Removed fsl_sub -q long.q because dont have SEG parallel capabilities set up

rm -r "$T1wFolder/$Subject" #Deleting the freesurfer folder that got copied over (leaving all else) GW


