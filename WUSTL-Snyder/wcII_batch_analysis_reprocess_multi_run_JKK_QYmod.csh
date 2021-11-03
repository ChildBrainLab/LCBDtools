#!/bin/csh

set wrkdir			= /data/nil-bluearc/shimony/wunder/wunder_caf_II
set subjects			= (neo323e_copy ) # neo342e neo503e neo504e neo508e) #neo262e neo267e neo318e) #neo288e neo290e ) #mal046 mal047 mal048 mal049 mal050 mal051 mal052 mal053) #mal033 mal034 mal035 mal030 mal031 mal032 ) #mal015) #mal026 mal027 mal028 mal029)  #mal012
cd $wrkdir
################
# batch preprocess
##################

foreach patid ($subjects)
	echo $patid

	pushd $patid	#			# into patid
	echo "set patid = " $patid 						>! $patid.params	#
	if ($status) exit $status
	/data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/generate_params_bold_pp_2013.csh DICOM.studies.txt		>> $patid.params	#
	/data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/constants_params.csh $patid				
	if ($status) exit $status	#
 #############
	cp /data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/bold_pp_2013_instructions ./$patid'_instructions'	#
	echo cp /data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/bold_pp_2013_instructions ./$patid'_instructions'	#


	#/data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/convert_to_nifti.csh $patid $mstd[1] $pstd[1]
	
	echo "here"

	source $patid.params	#
	@ num_bolds = ${#fstd}	#
#	
	if ( $num_bolds == 1 ) then	#
		set params = bold_pp_2013_multi_run.params	#
		set fc_params = bold_pp_2013fc_multi_run.params	#
	else if ( $num_bolds == 2) then	#
		set params = bold_pp_2013_multi_run_2.params	#
		set fc_params = bold_pp_2013fc_multi_run_2.params	#
	else if ( $num_bolds == 3) then	#
		set params = bold_pp_2013_multi_run_3.params	#
		set fc_params = bold_pp_2013fc_multi_run_3.params	#
	else if ( $num_bolds == 4) then	#
		set params = bold_pp_2013_multi_run_4.params	#
		set fc_params = bold_pp_2013fc_multi_run_4.params	#
	else if ( $num_bolds == 5) then	#
		set params = bold_pp_2013_multi_run_5.params	#
		set fc_params = bold_pp_2013fc_multi_run_5.params	#
	else if ( $num_bolds == 6) then	#
		set params = bold_pp_2013_multi_run_6.params	#
		set fc_params = bold_pp_2013fc_multi_run_6.params	#
	else if ( $num_bolds == 7) then	#
		set params = bold_pp_2013_multi_run_7.params	#
		set fc_params = bold_pp_2013fc_multi_run_7.params	#
	else if ( $num_bolds == 8) then	#
		set params = bold_pp_2013_multi_run_8.params	#
		set fc_params = bold_pp_2013fc_multi_run_8.params	#
	else	#
		echo "Error: Obscure number of bold runs.  You have ${#fstd} runs."	#
		exit	#
	endif	#
echo ""
	echo cat /data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/$params
	cat /data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/$params >> $patid.params
echo ""	#
	cat /data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/$fc_params >! $patid"fc".params

	date >! $patid'_cross_bold_pp_161012_FSL_ind_sefm.log'
	####/data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/cross_bold_pp_161012_JKK.csh $patid.params $patid'_instructions' >> $patid'_cross_bold_pp_161012_FSL_sfmc.log'
	/data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/cross_bold_pp_161012_JKK_ind_sefm_ind_BC.csh $patid.params $patid'_instructions' >> $patid'_cross_bold_pp_161012_FSL_ind_sefm.log'
	popd
echo ""
echo ""
echo " fcMRI preproc complete"
echo ""
echo ""
	
#	#################need to decide where the "three other files" go ~5/17/12 left in patid directory
	# pretty sure the below run_dvar code is obsolete given these various steps are done else where, but I'm leaving it for now kenleyj 8/13/15
stuff:
	date														>! $patid/$patid'_run_dvar.log'	#
	/data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/wcII_run_dvar_4dfp_multi_run_JKK_BC.csh $patid 	>> $patid/$patid'_run_dvar.log'	#
	if ($status) exit $status	#

	mv $patid/*atl.* ./$patid/QA


echo ""
echo ""
echo "Run dvar complete"
echo ""
echo ""
	
	# create necessary files for fciamge_analysis -v4 since the naming is hard coded in Jonathan Powers' scripts
	# should probably consider using symbolic links, but I don't know how links of links will work . . .
hey:
	pushd $patid
	source $patid.params

	if ($BiasField) then
		set BC = "_BC"
		echo "BC is "$BC
	else
		set BC = ""
	endif
	
	if (! ${?MB}) @ MB = 0			# skip slice timing correction and debanding
		set MBstr = _faln_dbnd
	if ($MB) set MBstr = ""
	@ i = 1
	while ( $i <= ${#fstd})
		pushd bold${i}
		foreach ending (img ifh hdr img.rec)
			cp -rp ${patid}'_b'$i${MBstr}'_xr3d'${BC}'_uwrp_atl'.4dfp.${ending} ${patid}_b${i}_xr3d_333.4dfp.${ending}
		end
		#cp -rp ${patid}_b{$i}_faln_dbnd_xr3d.mat ${patid}_b{$i}_xr3d.mat
		popd
		@ i++
	end

	pushd atlas
	cp $patid"_func_vols_ave_on_combined_7yo_target_111_333.4dfp.img" $patid"_anat_ave_t88_333.4dfp.img"
	cp $patid"_func_vols_ave_on_combined_7yo_target_111_333.4dfp.img.rec" $patid"_anat_ave_t88_333.4dfp.img.rec"
	cp $patid"_func_vols_ave_on_combined_7yo_target_111_333.4dfp.ifh" $patid"_anat_ave_t88_333.4dfp.ifh"
	cp $patid"_func_vols_ave_on_combined_7yo_target_111_333.4dfp.hdr" $patid"_anat_ave_t88_333.4dfp.hdr"
	#cp $patid"_func_vols_ave_on_TRIO_KY_NDC_333.4dfp.img" $patid"_anat_ave_t88_333.4dfp.img"
	#cp $patid"_func_vols_ave_on_TRIO_KY_NDC_333.4dfp.img.rec" $patid"_anat_ave_t88_333.4dfp.img.rec"
	#cp $patid"_func_vols_ave_on_TRIO_KY_NDC_333.4dfp.ifh" $patid"_anat_ave_t88_333.4dfp.ifh"
	#cp $patid"_func_vols_ave_on_TRIO_KY_NDC_333.4dfp.hdr" $patid"_anat_ave_t88_333.4dfp.hdr"
	popd	# out of atlas
	
	popd	#out of patid

	if ( ! -d freesurfer ) then
		mkdir freesurfer
	endif
	if ( ! -d freesurfer/$patid ) then
		pushd freesurfer
		mkdir $patid
		popd	# out of freesurfer directory
	endif
#echo ""
#	pwd
#echo ""
#exit
	if ( ! -d FREESURFER ) then
		mkdir FREESURFER
	endif
freeme:	
	# get number of mprs
	source $patid/$patid.params
	pushd $patid/atlas
		nifti_4dfp -n $patid"_mpr_n"${#mprs}"_111_t88" $patid"_mpr1T"	# freesurfer expects 711-2B 111 atlas registered images
									# that's not entirely true, actually we want to feed in
									# the atlas registered image so we get out atlas registered segmentations
		cp $patid"_mpr1T".nii ../../FREESURFER
	popd

end

