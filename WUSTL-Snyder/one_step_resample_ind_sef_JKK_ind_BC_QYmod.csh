#!/bin/tcsh -f
#$Header: /data/petsun4/data1/solaris/csh_scripts/RCS/one_step_resample.csh,v 1.1 2017/03/24 01:35:34 avi Exp $
#$Log: one_step_resample.csh,v $
# Revision 1.1  2017/03/24  01:35:34  avi
# Initial revision
#
set program = $0
set program = $program:t
set rcsid = '$Id: one_step_resample.csh,v 1.1 2017/03/24 01:35:34 avi Exp $'
echo $rcsid

if (${#argv} < 1) then
	echo "Usage:	$program <parameters file> [instructions]"
	echo "e.g.,	$program VB16168.params"
	exit 1
endif 
date
uname -a

set prmfile = $1
if (! -e $prmfile) then
	echo $prmfile not found
	exit -1
endif
source $prmfile
if (${#argv} > 1) then
	set instructions = $2
	if (! -e $instructions) then
		echo $program": "$instructions not found
		exit -1
	endif
	cat $instructions
	source $instructions
endif

setenv FSLOUTPUTTYPE NIFTI
###########################################
# compute unwarped EPI atlas transformation
###########################################
if (! ${?use_anat_ave}) @ use_anat_ave = 0
if ($use_anat_ave) then
	set epi_anat = $patid"_anat_ave"
else
	set epi_anat = $patid"_func_vols_ave"
endif
# moved the bold loop to a more outer portion so 
# I could reference individual spin echo field map
# epi_anat files; we will see.
@ k = 1
while ($k <= $#irun)
	# line below changed 
	#set epi_ref	= unwarp/${epi_anat}_uwrp	# I am not sure about the "b${k}"
	set epi_ref	= unwarp_${k}/${epi_anat}_uwrp_b${irun[$k]}
	if (! ${?outres}) @ outres = 333
	if (! ${?day1_patid}) set day1_patid = "";
	if ($day1_patid != "") then
		set patid1	= $day1_patid
		set t2wdir	= $day1_path
	else
		set patid1	= $patid
		set t2wdir	= atlas
	endif
	set atl_refs = (`ls $t2wdir/${patid1}_mpr_n?_${outres}_t88.4dfp.img $t2wdir/${patid1}_*_${outres}.4dfp.img`)
	if (${#atl_refs} < 1) then
		echo $program":" suitable $outres atlas space reference image not found
		exit -1
	endif
	set atl_ref	= $atl_refs[1]; set atl_ref = $atl_ref:r; set atl_ref = $atl_ref:r;
	#set xfm	= unwarp/${epi_anat}_uwrp_to_${target:t}
	set xfm		= unwarp_${k}/${epi_anat}_uwrp_b${irun[$k]}_to_${target:t}
	nifti_4dfp -n $atl_ref $atl_ref
	if ($status) exit $status
	if (! -e ${xfm}_t4) then
		echo ${xfm}_t4 not found
		exit -1
	endif
	if (! -e $epi_ref.4dfp.img || ! -e $epi_ref.4dfp.ifh) then
		echo $epi_ref not found
		exit -1
	endif
	if (! -e $epi_ref.nii) then
		nifti_4dfp -n $epi_ref $epi_ref
		if ($status) exit $status
	endif
	if (! -e $atl_ref.4dfp.img || ! -e $atl_ref.4dfp.ifh) then
		echo $atl_ref not found
		exit -1
	endif
	aff_conv 4f $epi_ref $atl_ref ${xfm}_t4 $epi_ref $atl_ref ${xfm}.mat
	if ($status) exit $status

	if (! ${?MB}) @ MB = 0			# skip slice timing correction and debanding
	set MBstr = _faln_dbnd
	if ($MB) set MBstr = ""
	if (! $?BiasField) set BiasField = 0
	if ($BiasField) then
		# altered below statement to allow for individual BC map
		#set BiasFieldMap = $patid${MBstr}_xr3d_avg_BF
		set BiasFieldMap = bold$irun[$k]/${patid}_b${irun[$k]}${MBstr}_xr3d_avg_BF
		# altered below line to allow for individual sefm
		# $FSLDIR/bin/applywarp --ref=$atl_ref --postmat=${xfm}.mat --warp=unwarp/${epi_anat}_uwrp_shift_warp.nii.gz \
		#	--in=$BiasFieldMap --out=${BiasFieldMap}_on_${target:t} --interp=spline
		$FSLDIR/bin/applywarp --ref=$atl_ref --postmat=${xfm}.mat --warp=unwarp_${k}/${epi_anat}_uwrp_shift_warp.nii.gz \
			--in=$BiasFieldMap --out=${BiasFieldMap}_on_${target:t} --interp=spline
		if ($status) exit $status
		set BFCstr = "-mul ${BiasFieldMap}_on_${target:t}"
	else 
		set BFCstr = ""
	endif
	######################################################################
	# get a nifti volume for each frame post frame alignment and debanding
	######################################################################
	set epi = bold$irun[$k]/$patid"_b"$irun[$k]${MBstr}
	nifti_4dfp -n $epi $epi
	if ($status) exit $status
	$FSLDIR/bin/fslsplit $epi $epi -t
	###################
	# Unwarp bias field
	###################
	if ($BiasField) then
		set norm_file = ${epi}_xr3d_BC_avg_norm.4dfp.img.rec
	else 
		set norm_file = ${epi}_r3d_avg_norm.4dfp.img.rec
	endif
	####################################
	# get mode 1000 normalization factor
	####################################
	if (! -e $norm_file) then
		echo $norm_file not found
		exit -1
	endif
	set f = `head $norm_file | awk '/original/{print 1000/$NF}'`

	@ i = 0; echo | awk '{printf ("Resampling frame:")}'
	while ($i < `fslval $epi dim4`)
		set padded = `printf "%04i" ${i}`
		@ j = $i + 1
		echo $j | awk '{printf (" %d", $1)}'
		#######################
		# extract xr3d.mat file
		#######################
		grep -x -A4 "t4 frame $j" ${epi}_xr3d.mat | tail -4 >! ${epi}_tmp_t4
		grep -x -A6 "t4 frame $j" ${epi}_xr3d.mat | tail -1 >> ${epi}_tmp_t4
		########################################
		# run affine convert on extracted matrix
		########################################
		aff_conv xf $epi $epi ${epi}_tmp_t4 ${epi}$padded ${epi}$padded ${epi}_tmp.mat > /dev/null
		if ($status) exit $status
	#######################################
	# apply all transformations in one step
	#######################################
		$FSLDIR/bin/applywarp --ref=$atl_ref --premat=${epi}_tmp.mat --postmat=${xfm}.mat --warp=unwarp_${k}/${epi_anat}_uwrp_shift_warp.nii.gz \
		--in=${epi}$padded --out=${epi}_on_${target:t}$padded --interp=spline
		if ($status) exit $status
		@ i++		# next frame
	end
	################################################################
	# merge the split volumes and then do 4d intensity normalization
	################################################################
	fslmerge -t ${epi}_xr3d_uwrp_atl ${epi}_on_${target:t}????.nii
	fslmaths ${epi}_xr3d_uwrp_atl -mul $f $BFCstr ${epi}_xr3d_uwrp_atl
	if ($status) exit $status
	#####################################################
	# convert final result back to 4dfp and then clean up
	#####################################################
echo ""
echo "I believe error is here"
echo ""
	if ($BiasField) then
		nifti_4dfp -4		${epi}_xr3d_uwrp_atl ${epi}_xr3d_BC_uwrp_atl
		ifh2hdr -r2000		${epi}_xr3d_BC_uwrp_atl
		set_undefined_4dfp	${epi}_xr3d_BC_uwrp_atl		# set undefined voxels (lost by passage through NIfTI) to 1.e-37
		/bin/rm ${epi}.nii ${epi}????.nii ${epi}_xr3d_uwrp_atl.nii ${epi}_on_${target:t}????.nii ${epi}_tmp.mat ${epi}_tmp_t4
	else
		nifti_4dfp -4		${epi}_xr3d_uwrp_atl ${epi}_xr3d_uwrp_atl
		ifh2hdr -r2000		${epi}_xr3d_uwrp_atl
		set_undefined_4dfp	${epi}_xr3d_uwrp_atl		# set undefined voxels (lost by passage through NIfTI) to 1.e-37
		/bin/rm ${epi}.nii ${epi}????.nii ${epi}_xr3d_uwrp_atl.nii ${epi}_on_${target:t}????.nii ${epi}_tmp.mat ${epi}_tmp_t4 
	endif
	@ k++			# next fMRI run
end
if ($BiasField) then
	/bin/rm -f ${BiasFieldMap}_on_${target:t}.nii
endif
exit 0
