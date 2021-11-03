#!/bin/bash

#preproc_dirs="/data/sylvester/data1/social_anxiety/preproc/se/mb4_2.4/"
#dirs=("/data/sylvester/data1/npad/preproc/se/mb4_2.4/" "/data/sylvester/data1/npad/preproc/se/mb4_2.4/new_pipeline_bak" "/data/sylvester/data1/npad/preproc/se/mb4_2.4/old_pipeline")

patid=$1

rm $preproc_dir/$patid/bold*/*uwrp.4dfp.*
rm $preproc_dir/$patid/bold*/*uwrp.nii*
rm $preproc_dir/$patid/bold*/*BC_norm.4dfp*
rm $preproc_dir/$patid/bold*/*BC.4dfp*
rm $preproc_dir/$patid/bold*/*faln_dbnd_xr3d.4dfp*
rm $preproc_dir/$patid/bold*/*faln_dbnd_orig.4dfp*
rm $preproc_dir/$patid/bold*/*faln_dbnd.4dfp*
rm $preproc_dir/$patid/bold*/*faln.4dfp*
rm $preproc_dir/$patid/bold*/*Task??.4dfp*
rm $preproc_dir/$patid/bold*/*with_extra*

rm $preproc_dir/$patid/unwarp*/*_BC_uwrp.nii.gz
rm $preproc_dir/$patid/unwarp*/*_BC.nii.gz
rm $preproc_dir/$patid/unwarp*/*_BC.4dfp*

