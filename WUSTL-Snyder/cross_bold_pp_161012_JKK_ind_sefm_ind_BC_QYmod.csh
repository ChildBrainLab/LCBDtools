#!/bin/csh -x
#$Header: /data/petsun4/data1/solaris/csh_scripts/RCS/cross_bold_pp_161012.csh,v 1.12 2018/04/11 22:37:59 avi Exp $
#$Log: cross_bold_pp_161012.csh,v $
# Revision based on JKK's version
# removed -x from #!/bin/csh -x
# able to do task runs with individual field map & bias field correction -QY
#
# Revision 1.12  2018/04/11  22:37:59  avi
# -seqstr
#
# Revision 1.11  2017/12/26  23:45:33  avi
# trap sefm_pp_AZS.csh errors
#
# Revision 1.10  2017/07/08  04:33:25  avi
# extensive revision to accommodate field map correction using sefm
#
# Revision 1.9  2017/06/14  05:37:33  avi
# initialize  ${patid}${MBstr}_xr3d.lst for appending
#
# Revision 1.8  2017/04/26  01:16:25  avi
# correct anat_ave creation bug
#
# Revision 1.7  2017/03/22  22:14:07  avi
# extensive new code to implement bias field correction ($BiasField != 0)
#
# Revision 1.6  2016/11/07  01:49:44  avi
# correct bug that would emerge with axial MP-RAGE data
#
# Revision 1.5  2016/11/01  00:26:31  avi
# bring FD logic into liine with fcMRI_preproc_161012.csh logic
# lomotil logic
#
# Revision 1.4  2016/10/25  21:32:46  avi
# correct $day1_path bug
#
# Revision 1.3  2016/10/25  00:18:04  avi
# modified FD logic
#
# Revision 1.2  2016/10/17  23:57:23  avi
# correct several minor errors
#
# Revision 1.1  2016/10/12  20:10:54  avi
# Initial revision
#
# Revision 1.14  2016/08/12  00:06:04  avi
# perform dcm2nii if measured field mapping studies are listed in $gre()
#
# Revision 1.13  2016/06/12  02:28:39  avi
# use $fmtfile instead of $format in all calls to actmapf_4dfp, var_4dfp, and format2lst
#
# Revision 1.12  2016/06/01  00:38:29  avi
# new params variable $MBfac
#
# Revision 1.11  2016/05/16  22:59:29  avi
# correct typo
#
# Revision 1.10  2016/05/16  21:40:09  avi
# prevent accumulation over repeat script invocations of format specification for func_vols_ave
#
# Revision 1.9  2015/06/08  05:31:30  avi
# accommodate not defining $anat_avet in params
#
# Revision 1.8  2014/07/15  02:20:27  avi
# cross-day fucntional in cases with t2w data
#
# Revision 1.7  2014/07/11  01:01:53  avi
# smoother Et2w logic
#
# Revision 1.6  2014/03/12  22:29:20  avi
# code working for measured field maps
#
# Revision 1.5  2014/02/22  07:40:34  avi
# $min_frames instead of hard coded 240
#
# Revision 1.4  2014/02/21  07:00:51  avi
# correct minor bug in computation of ${patid}_func_vols
#
# Revision 1.3  2014/02/21  04:39:14  avi
# handle cross-day data (but t2w must be in current atlas directory)
#
# Revision 1.2  2013/11/08  06:23:59  avi
# optional pre-blur (parameter $anat_aveb) on func_vols run_dvar_4dfp
#
# Revision 1.1  2013/11/08  05:38:02  avi
# Initial revision
#

set idstr = '$Id: cross_bold_pp_161012.csh,v 1.12 2018/04/11 22:37:59 avi Exp $'
echo $idstr
set program = $0:t
echo $program $argv[1-]

if (${#argv} < 1) then
	echo "usage:	"$program" params_file [instructions_file]"
	exit 1
endif
set prmfile = $1
echo "prmfile="$prmfile

if (! -e $prmfile) then
	echo $program": "$prmfile not found
	exit -1
endif
source $prmfile
set instructions = ""
if (${#argv} > 1) then
	set instructions = $2
	if (! -e $instructions) then
		echo $program": "$instructions not found
		exit -1
	endif
	cat $instructions
	source $instructions
endif

##########
# check OS
##########
set OS = `uname -s`
if ($OS != "Linux") then
	echo $program must be run on a linux machine
	exit -1
endif

if ($target:h != $target) then
	set tarstr = -T$target
else
	set tarstr = $target
endif

@ runs = ${#irun}
if ($runs != ${#fstd}) then
	echo "irun fstd mismatch - edit "$prmfile
	exit -1
endif

if (! ${?scrdir}) set scrdir = ""
@ usescr = `echo $scrdir | awk '{print length ($1)}'`
if ($usescr) then 
	if (! -e $scrdir) mkdir $scrdir
	if ($status) exit $status
endif
set sourcedir = $cwd
if (! ${?sorted}) @ sorted = 0

if (! ${?MB}) @ MB = 0			# skip slice timing correction and debanding
set MBstr = _faln_dbnd
if ($MB) set MBstr = ""

set squeezestr = ""
if (${?sx}) then
	set squeezestr = $squeezestr" -sx"$sx
endif
if (${?sy}) then
	set squeezestr = $squeezestr" -sy"$sy
endif

if (! ${?E4dfp}) @ E4dfp = 0
if (${E4dfp}) then
	echo "4dfp files have been pre-generated. Option E4dfp set with value $E4dfp. Skipping dcm_to_4dfp"
endif

if (! ${?use_anat_ave}) @ use_anat_ave = 0
if ($use_anat_ave) then
	set epi_anat = $patid"_anat_ave"
else
	set epi_anat = $patid"_func_vols_ave"
endif
#if (! ${?min_frames}) @ min_frames = 240
# MM mod because a subject failed
if (! ${?min_frames}) @ min_frames = 190
if (! ${?day1_patid}) set day1_patid = "";
if ($day1_patid != "") then
	set patid1	= $day1_patid
	set day1_path	= `echo $day1_path | sed 's|/$||g'`
else
	set patid1	= $patid
endif

if (${?goto_UNWARP}) goto UNWARP

date
###################
# process BOLD data
###################
if (${?epi_zflip}) then
	if ($epi_zflip) set zflip = "-z"
else
	set zflip = ""
endif
if (! ${?interleave}) set interleave = ""
if (${?Siemens_interleave}) then
	if ($Siemens_interleave) set interleave = "-N"
endif
if (! ${?MBfac}) @ MBfac = 1
if (! ${?seqstr}) then
	set STR = "";
else
	set STR = "-seqstr "$seqstr;
endif

@ err = 0
@ k = 1
while ($k <= $runs)
	if (! $E4dfp) then
		if ($usescr) then		# test to see if user requested use of scratch disk
			if (-e bold$irun[$k]) /bin/rm bold$irun[$k]	# remove existing link
			if (! -d $scrdir/bold$irun[$k]) mkdir $scrdir/bold$irun[$k]
			ln -s $scrdir/bold$irun[$k] bold$irun[$k]
		else
			if (! -d bold$irun[$k]) mkdir bold$irun[$k]
		endif
	endif
	pushd bold$irun[$k]
	set y = $patid"_b"$irun[$k]${MBstr}
	if (-e $y.4dfp.img && -e $y.4dfp.ifh) goto POP
	if (! $E4dfp) then
		if ($sorted) then
			echo		dcm_to_4dfp -q -b study$fstd[$k] $inpath/study$fstd[$k]
			if ($go)	dcm_to_4dfp -q -b study$fstd[$k] $inpath/study$fstd[$k]
		else
			echo		dcm_to_4dfp -q -b study$fstd[$k] $inpath/$dcmroot.$fstd[$k]."*"
			if ($go)	dcm_to_4dfp -q -b study$fstd[$k] $inpath/$dcmroot.$fstd[$k].*
		endif
	endif
	if (${?nounpack}) goto FA
	echo		unpack_4dfp -V study$fstd[$k] $patid"_b"$irun[$k] -nx$nx -ny$ny $squeezestr $zflip
	if ($go)	unpack_4dfp -V study$fstd[$k] $patid"_b"$irun[$k] -nx$nx -ny$ny $squeezestr $zflip

####################################################3
# MM mod: uncommenting the below
	set ifh = $patid"_b"$irun[$k].4dfp.ifh
	set num_slices = `cat $ifh | grep -F 'matrix size [3]' | cut -d "=" -f2`
	@ num_slices = $num_slices
	# adding code to create string output from dicom files so we can order thing correctly because Siemens Interleave doesn't work with MB
	pushd $inpath/study$fstd[$k]		# into fcMRI study folder
	set dicom_file = `ls -lrt *dcm | tail -1 | awk '{print $11}'`	# this will get the file itself, not the linked file (good in case links are broken)
#	set start_line = `strings $dicom_file | grep -n MosaicRefAcqTimes | cut -d ":" -f1`	# this provides me the line where the phrase MosaicRefAcqTimes is, if I add one
	set start_line = `strings $dicom_file | grep -ne '^MosaicRefAcqTimes$' -A12 | perl -ne 'if (/^(\d+)-\d+\.\d+$/) { print $1; exit }'`
#	@ start_line = $start_line + 1						# then I will be on the starting line of the times
	set end_line = `strings $dicom_file | grep -n AutoInlineImageFilterEnabled | cut -d ":" -f1`	# this is the category that occured after the times, need to check this is
	@ end_line = $end_line - 1							# always true, subtract 1 to get the last time
	# now grab only the lines you actually want from the dicom file containing the times
	strings $dicom_file | sed -n "${start_line},${end_line}p" | head -17 >! ../bold$irun[$k]/bold$irun[$k]_timing.lst
	set squeezy = `cat ../bold$irun[$k]/bold$irun[$k]_timing.lst | gawk '{print NR, $1}' | sort -n -k 2,2 | gawk '{printf("%d,", $1);}'`
	set squeezy = `echo $squeezy | rev | cut -d "," -f2-200 | rev`				# this only allows for 199 slices so if this may
												# need to be altered based on that information
												# not sure if this is the correct variable
												# part of the frame_align_4dfp command below
												# but it's not defined any where else
												# it is the same thing, before I searched for $STR
												# which won't result in a match for set STR = ...
	set STR = "-seqstr "$squeezy
echo $STR
popd		# out of fcMRI study folder
	if ($status) then
		@ err++
		/bin/rm $patid"_b"$irun[$k]*
		goto POP
	endif
	echo		/bin/rm  study$fstd[$k]."*"
	if ($go)	/bin/rm  study$fstd[$k].*
FA:
	echo "MM TEMP!!!!!!!!!!!!!!!!!!!!!!!"
	echo "MM TEMP!!!!!!!!!!!!!!!!!!!!!!!"
	echo "MM TEMP!!!!!!!!!!!!!!!!!!!!!!!"
	pwd
	if ($MB) goto POP
	#echo		frame_align_4dfp $patid"_b"$irun[$k] $skip -TR_vol $TR_vol -TR_slc $TR_slc -d $epidir $interleave -m $MBfac $STR
	#if ($go)	frame_align_4dfp $patid"_b"$irun[$k] $skip -TR_vol $TR_vol -TR_slc $TR_slc -d $epidir $interleave -m $MBfac $STR
# do you need interleave and seqstr
	echo		frame_align_4dfp $patid"_b"$irun[$k] $skip -TR_vol $TR_vol -TR_slc $TR_slc -d $epidir $interleave -m $MBfac $STR
	if ($go)	frame_align_4dfp $patid"_b"$irun[$k] $skip -TR_vol $TR_vol -TR_slc $TR_slc -d $epidir $interleave -m $MBfac $STR

	echo		deband_4dfp -n$skip $patid"_b"$irun[$k]"_faln"
	if ($go)	deband_4dfp -n$skip $patid"_b"$irun[$k]"_faln"
	if ($status)	exit $status

	if ($economy > 2) then
		echo		/bin/rm $patid"_b"$irun[$k].4dfp."*"
		if ($go)	/bin/rm $patid"_b"$irun[$k].4dfp.*
	endif
	if ($economy > 3) then
		echo		/bin/rm $patid"_b"$irun[$k]"_faln".4dfp."*"
		if ($go)	/bin/rm $patid"_b"$irun[$k]"_faln".4dfp.*
	endif
POP:
	popd	# out of bold$irun[$k]
	@ k++
end
if ($err) then
	echo $program": one or more BOLD runs failed preliminary processing"
	exit -1
endif
if ($epi2atl == 2) goto ATL

if (-e  $patid"_xr3d".lst)	/bin/rm $patid"_xr3d".lst;	touch $patid"_xr3d".lst
@ k = 1
while ($k <= $runs)
	echo bold$irun[$k]/$patid"_b"$irun[$k]${MBstr} >>	$patid"_xr3d".lst
	@ k++
end

echo cat	$patid"_xr3d".lst
cat		$patid"_xr3d".lst
echo		cross_realign3d_4dfp -n$skip -qv$normode -l$patid"_xr3d".lst
if ($go)	cross_realign3d_4dfp -n$skip -qv$normode -l$patid"_xr3d".lst
if ($status)	exit $status

set instructions = ""
if (${#argv} > 1) then
	set instructions = $2
	if (! -e $instructions) then
		echo $program": "$instructions not found
		exit -1
	endif
	cat $instructions
	source $instructions
endif


##############################################
# bias field correct (if no prescan normalize)
##############################################
if (! $?BiasField)  @ BiasField = 0;
if ($BiasField) then
# create average across all runs	
	###if (-e ${patid}${MBstr}_xr3d.lst) /bin/rm ${patid}${MBstr}_xr3d.lst
	###touch ${patid}${MBstr}_xr3d.lst
	###@ k = 1
	###while ($k <= $runs)
	###	echo bold$irun[$k]/$patid"_b"$irun[$k]${MBstr}_xr3d >> ${patid}${MBstr}_xr3d.lst
	###	@ k++
	###end
	# commented lines ~322-328 out because I created the xr3d list above that is tailored for this code
# altering previous lines to accomodate doing each bold run individually (sp?)
	@ q = 1
	while ($q <= ${#fstd})
		touch ${patid}_b$irun[$q]${MBstr}_xr3d.lst
		echo bold$irun[$q]/$patid"_b"$irun[$q]${MBstr} >> ${patid}_b$irun[$q]${MBstr}_xr3d.lst
		#conc_4dfp  ${patid}${MBstr}_xr3d -l${patid}${MBstr}_xr3d.lst
		conc_4dfp  ${patid}_b$irun[$q]${MBstr}_xr3d -l${patid}_b$irun[$q]${MBstr}_xr3d.lst
		set format = `conc2format ${patid}_b$irun[$q]${MBstr}_xr3d.conc $skip`	
		actmapf_4dfp $format ${patid}_b$irun[$q]${MBstr}_xr3d.conc -aavg
		if ($status) exit $status
		set base = ${patid}_b$irun[$q]${MBstr}_xr3d_avg
		niftigz_4dfp -n ${base} ${base}
		if ($status) exit $status
		$FSLDIR/bin/bet ${base} ${base}_brain -f 0.3
		if ($status) exit $status
	# compute bias field within brain mask
		$FSLDIR/bin/fast -t 2 -n 3 -H 0.1 -I 4 -l 20.0 --nopve -B -o ${base}_brain ${base}_brain
		if ($status) exit $status
		niftigz_4dfp -4 ${base}_brain_restore ${base}_brain_restore
		if ($status) exit $status
	# compute extended bias field
		extend_fast_4dfp -G ${base} ${base}_brain_restore ${base}_BF
		if ($status) exit $status
		niftigz_4dfp -n ${base}_BF ${base}_BF
		if ($status) exit $status
		#@ m = 1
		#while ($m <= ${#fstd})
		pushd bold$irun[$q]
		# bias field correct the whole run
		echo imgopr_4dfp -p$patid"_b"$irun[$q]${MBstr}_xr3d_BC $patid"_b"$irun[$q]${MBstr}_xr3d ../${base}_BF
		imgopr_4dfp -p$patid"_b"$irun[$q]${MBstr}_xr3d_BC $patid"_b"$irun[$q]${MBstr}_xr3d ../${base}_BF 
		if ($status) exit $status
			#####/bin/rm -r   $patid"_b"$irun[$k]${MBstr}_xr3d.4dfp* 	# this step removes the non bias field corrected data;
											# for testing purposes, I'd like to leave it, but once
											# I am finished testing, it will be removed for 
											# comparison purposes
		popd
		mv *"_b"$irun[$q]* ./"bold"$irun[$q]
			#@ m++	
		#end
		if ($status) exit $status
	@ q++
end
	set BC = "_BC"
else 
	set BC = ""
endif

date
#################################
# compute mode 1000 normalization
#################################
@ k = 1
while ($k <= $runs)
	pushd bold$irun[$k]
	if ($BiasField) then 
		set format = `cat $patid"_b"$irun[$k]${MBstr}_xr3d_BC.4dfp.ifh | \
			gawk 'BEGIN{skip = 1} {if  (/\[4\]/) {f = $NF}} END{printf("%dx%d+",skip,f-skip)}' skip=$skip`
		actmapf_4dfp $format $patid"_b"$irun[$k]${MBstr}_xr3d_BC -aavg 
		if ($status) exit $status		
		echo 		normalize_4dfp $patid"_b"$irun[$k]${MBstr}_xr3d_BC_avg -h
		if ($go)	normalize_4dfp $patid"_b"$irun[$k]${MBstr}_xr3d_BC_avg -h
		if ($status) exit $status	
		if ($economy > 4 && $epi2atl == 0) /bin/rm $patid"_b"$irun[$k]${MBstr}_xr3d_BC_avg.4dfp."*"
	else 
		echo 		normalize_4dfp $patid"_b"$irun[$k]${MBstr}"_r3d_avg" -h	
		if ($go)	normalize_4dfp $patid"_b"$irun[$k]${MBstr}"_r3d_avg" -h
		if ($status) exit $status	
		if ($economy > 4 && $epi2atl == 0) /bin/rm $patid"_b"$irun[$k]${MBstr}"_r3d_avg".4dfp."*"
	endif
	popd	# out of bold$irun[$k]
	@ k++
end

date
###############################
# apply mode 1000 normalization
###############################
if (-e  $patid"_anat".lst) /bin/rm $patid"_anat".lst; touch $patid"_anat".lst
@ k = 1
while ($k <= $runs)
	pushd bold$irun[$k]
	if ($BiasField) then
		set file = $patid"_b"$irun[$k]${MBstr}_xr3d_BC_avg_norm.4dfp.img.rec
	else 
		set file = $patid"_b"$irun[$k]${MBstr}_r3d_avg_norm.4dfp.img.rec
	endif
	set f = 1.0; if (-e $file) set f = `head $file | awk '/original/{print 1000/$NF}'`
	echo		scale_4dfp $patid"_b"$irun[$k]${MBstr}_xr3d${BC} $f -anorm
	if ($go)	scale_4dfp $patid"_b"$irun[$k]${MBstr}_xr3d${BC} $f -anorm
	echo		/bin/rm $patid"_b"$irun[$k]${MBstr}_xr3d${BC}.4dfp."*"
	if ($go)	/bin/rm $patid"_b"$irun[$k]${MBstr}_xr3d${BC}.4dfp.*
	popd	# out of bold$irun[$k]
	echo bold$irun[$k]/$patid"_b"$irun[$k]${MBstr}_xr3d${BC}_norm >>	$patid"_anat".lst	
	if ($BiasField) /bin/rm $patid"_b"$irun[$k]${MBstr}_xr3d_BC_avg_norm.4dfp.*
	@ k++
end
/bin/cp $patid"_anat".lst $patid"_func_vols".lst

date
###################
# movement analysis
###################
if (! -d movement) mkdir movement
if (! ${?lomotil}) then
	set lstr = ""
else
	set lstr = "-l$lomotil TR_vol=$TR_vol"
endif
@ k = 1
while ($k <= $runs)
	echo		mat2dat bold$irun[$k]/"*_xr3d".mat -RD -n$skip $lstr
	if ($go)	mat2dat bold$irun[$k]/*"_xr3d".mat -RD -n$skip $lstr
	echo		/bin/mv bold$irun[$k]/"*_xr3d.*dat"	movement
	if ($go)	/bin/mv bold$irun[$k]/*"_xr3d".*dat	movement
	@ k++
end

date

if (! -d atlas) mkdir atlas
if ($BiasField) then
	/bin/mv ${base}_brain.* ${base}_brain_restore.* atlas/
endif
######################################
# make EPI first frame (anatomy) image
######################################
echo cat	$patid"_anat".lst
cat		$patid"_anat".lst
echo		paste_4dfp -p1 $patid"_anat".lst	$patid"_anat_ave"
if ($go)	paste_4dfp -p1 $patid"_anat".lst	$patid"_anat_ave"
echo		ifh2hdr	-r2000				$patid"_anat_ave"
if ($go)	ifh2hdr	-r2000				$patid"_anat_ave"
echo		/bin/mv $patid"_anat*" atlas
if ($go)	/bin/mv $patid"_anat"* atlas

#######################################
# make func_vols_ave using actmapf_4dfp
#######################################
echo	conc_4dfp ${patid}_func_vols -l${patid}_func_vols.lst
	conc_4dfp ${patid}_func_vols -l${patid}_func_vols.lst
if ($status) exit $status
cat			${patid}_func_vols.conc
echo		/bin/mv	${patid}_func_vols."*" atlas
if ($go)	/bin/mv	${patid}_func_vols.*   atlas

pushd movement
if (-e ${patid}${MBstr}"_xr3d".FD) /bin/rm	${patid}${MBstr}"_xr3d".FD
touch						${patid}${MBstr}"_xr3d".FD
@ k = 1
while ($k <= $runs)
	gawk -f $RELEASE/FD.awk $patid"_b"$irun[$k]${MBstr}"_xr3d".ddat >> ${patid}${MBstr}"_xr3d".FD
	@ k++
end
if ($?FDthresh) then 
	if (! $?FDtype) set FDtype = 1
	conc2format ../atlas/${patid}_func_vols.conc $skip | xargs format2lst > $$.format0
	gawk '{c="+";if ($'$FDtype' > crit)c="x"; printf ("%s\n",c)}' crit=$FDthresh ${patid}${MBstr}"_xr3d".FD > $$.format1
	paste $$.format0 $$.format1 | awk '{if($1=="x")$2="x";printf("%s",$2)}' > ${patid}${MBstr}"_xr3d".FD.format
	/bin/rm $$.format0 $$.format1
	/bin/mv ${patid}${MBstr}"_xr3d".FD.format ../atlas/
endif 
popd	

pushd atlas		# into atlas
if (! ${?anat_aveb}) set anat_aveb = 0.
if (! ${?anat_avet}) then			# set anat_avet excessively high if you wish not to use DVARS as a frame censoring technique 
	set xstr = ""				# compute threshold using find_dvar_crit.awk
else
	set xstr = -x$anat_avet
endif
set  format = `conc2format ${patid}_func_vols.conc $skip`	
echo $format >! ${patid}_func_vols.format	
echo	actmapf_4dfp ${patid}_func_vols.format ${patid}_func_vols.conc -aave_tmp
	actmapf_4dfp ${patid}_func_vols.format ${patid}_func_vols.conc -aave_tmp
if ($status) exit $status
nifti_4dfp -n ${patid}_func_vols_ave_tmp ${patid}_func_vols_ave_tmp
$FSLDIR/bin/bet ${patid}_func_vols_ave_tmp.nii ${patid}_func_vols_ave_tmp_msk -f 0.3
if ($status) exit $status
niftigz_4dfp -4  ${patid}_func_vols_ave_tmp_msk.nii.gz  ${patid}_func_vols_ave_tmp_msk
echo	run_dvar_4dfp ${patid}_func_vols.conc -m${patid}_func_vols_ave_tmp_msk -n$skip $xstr -b$anat_aveb
	run_dvar_4dfp ${patid}_func_vols.conc -m${patid}_func_vols_ave_tmp_msk -n$skip $xstr -b$anat_aveb
if ($status) exit $status	
rm  ${patid}_func_vols_ave_tmp*
if ($?FDthresh) then 
	format2lst ${patid}_func_vols.format > $$.format1
	format2lst ${patid}${MBstr}"_xr3d".FD.format > $$.format2
	paste $$.format1 $$.format2 | gawk '{if($1=="x")$2="x";printf("%s",$2);}' | xargs condense  > ${patid}_func_vols.format
	rm $$.format1 $$.format2
endif

set str = `format2lst -e ${patid}_func_vols.format | gawk '{k=0;l=length($1);for(i=1;i<=l;i++)if(substr($1,i,1)=="x")k++;}END{print k, l;}'`
echo "$str[1] out of $str[2] frames fails user's frame rejection criterion"
@ j = $str[2] - $str[1]; if ($j < $min_frames) exit 1	# require at least $min_frames below FD and/or dvar threshold to proceed

actmapf_4dfp ${patid}_func_vols.format ${patid}_func_vols.conc -aave
if ($status) exit $status

if ($day1_patid != "") then
##########################################
# compute cross-day $epi_anat registration
##########################################
	set stretch_flag = ""
	if (! ${?cross_day_nostretch}) @ cross_day_nostretch = 0;
	if ($cross_day_nostretch) set stretch_flag = -nostretch
	if ($use_anat_ave) then
		set trailer = anat_ave
	else
		set trailer = func_vols_ave
	endif
	echo		cross_day_imgreg_4dfp $patid $day1_path $day1_patid $tarstr $stretch_flag -a$trailer
	if ($go)	cross_day_imgreg_4dfp $patid $day1_path $day1_patid $tarstr $stretch_flag -a$trailer
	if ($status) exit $status
	if ($trailer != anat_ave) then
		/bin/rm -f						${patid}_anat_ave_to_${target:t}_t4 
		ln -s $cwd/${patid}_func_vols_ave_to_${target:t}_t4	${patid}_anat_ave_to_${target:t}_t4
	endif
	@ Et2w = 0
	if (-e $day1_path/$patid1"_t2wT".4dfp.img) then
		set t2w = $patid1"_t2wT"
		@ Et2w = 1
	else if (-e $day1_path/$patid1"_t2w".4dfp.img) then
		set t2w = $patid1"_t2w"
		@ Et2w = 1
	endif 
	if (-e $day1_path/$patid1"_mpr1T".4dfp.img) then 
		set mpr = $patid1"_mpr1T"
	else if ( -e $day1_path/$patid1"_mpr1".4dfp.img) then
		set mpr = $patid1"_mpr1"
	else 
		echo "no structual image in day1_path"
		exit 1
	endif
	if ($day1_path != $cwd) then
		/bin/cp -t . \
			$day1_path/${day1_patid}_${trailer}_to_*_t4 \
			$day1_path/${mpr}.4dfp.* \
			$day1_path/${mpr}_to_${target:t}_t4 
		if ($status) exit $status
	endif
	if ($Et2w) then
		echo "t2w="$t2w
		if ($day1_path != $cwd) then
			/bin/cp $day1_path/${t2w}.4dfp.* $day1_path/${t2w}_to_${target:t}_t4 .
			if ($status) exit $status
		endif
		t4_mul ${epi_anat}_to_${day1_patid}_${trailer}_t4 ${day1_patid}_${trailer}_to_${t2w}_t4 ${epi_anat}_to_${t2w}_t4
		if ($status) exit $status
		t4_mul ${epi_anat}_to_${t2w}_t4 ${t2w}_to_${target:t}_t4
		if ($status) exit $status
	else
		t4_mul ${epi_anat}_to_${day1_patid}_${trailer}_t4 ${day1_patid}_${trailer}_to_${mpr}_t4 ${epi_anat}_to_${mpr}_t4
		if ($status) exit $status
		if ( $day1_path != $cwd  && (! ${?gre} && ! ${?FMmag}) && $?FMmean && $?FMbases ) then 
			/bin/cp -t . \
				$day1_path/${patid1}_aparc+aseg_on_${target:t}_333.4dfp.* \
				$day1_path/${patid1}_FSWB_on_${target:t}_333.4dfp.* \
				$day1_path/${patid1}_CS_erode_on_${target:t}_333_clus.4dfp.* \
				$day1_path/${patid1}_WM_erode_on_${target:t}_333_clus.4dfp.* \
				$day1_path/${patid1}_aparc+aseg.4dfp.* \
				$day1_path/${patid1}_orig_to_${mpr}_t4
			if ($status) exit $status
		endif
	endif 
	goto EPI_to_ATL
endif
######################
# make MP-RAGE average
######################
@ nmpr = ${#mprs}
if ($nmpr < 1) exit 0
set mprave = $patid"_mpr_n"$nmpr
set mprlst = ()
@ k = 1
while ($k <= $nmpr)
	if (! $E4dfp) then
		if ($sorted) then
			echo		dcm_to_4dfp -b $patid"_mpr"$k $inpath/study$mprs[$k]
			if ($go)	dcm_to_4dfp -b $patid"_mpr"$k $inpath/study$mprs[$k]
		else
			echo		dcm_to_4dfp -b $patid"_mpr"$k $inpath/$dcmroot.$mprs[$k]."*"
			if ($go)	dcm_to_4dfp -b $patid"_mpr"$k $inpath/$dcmroot.$mprs[$k].*
		endif
		if ($status) exit $status
	endif
	set mprlst = ($mprlst $patid"_mpr"$k)
	@ k++
end

date
#########################
# compute atlas transform
#########################
if (! ${?tse}) 	set tse = ()
if (! ${?t1w})	set t1w = ()
if (! ${?pdt2})	set pdt2 = ()
if (! ${?Gad})	set Gad = 0;		# Gadolinium contrast given: @ Gad = 1

if ($#tse == 0 && ! ${?FMmag} && ! ${?gre}) then
	set mprlstT = ()
		foreach mpr ($mprlst)  
		@ ori = `awk '/orientation/{print $NF}' ${mpr}.4dfp.ifh`
		switch ($ori)
		case 2:
					set mprlstT = ($mprlstT ${mpr});  breaksw;
		case 3:
			C2T_4dfp $mpr;	set mprlstT = ($mprlstT ${mpr}T); breaksw;
		case 4:
			S2T_4dfp $mpr;	set mprlstT = ($mprlstT ${mpr}T); breaksw;
		default:
			echo $program": illegal "$mpr" orientation"; exit -1; breaksw;
		endsw
	end
	set mprlst = ($mprlstT)
endif 

set mpr = $mprlst[1]
if ($Gad) then
	mpr2atl1_4dfp $mpr $tarstr useold
	if ($status) exit $status
	set episcript = epi2t2w2mpr2atl3_4dfp;
else
	echo		avgmpr_4dfp $mprlst $mprave $tarstr useold
	if ($go)	avgmpr_4dfp $mprlst $mprave $tarstr useold
	if ($status) exit $status
	set episcript = epi2t2w2mpr2atl2_4dfp;
endif
foreach O (111 222 333)
	ifh2hdr -r1600 ${patid}_mpr_n${nmpr}_${O}_t88
end

@ ntse = ${#tse}
if (${#t1w}) then
	if (! $E4dfp) then
		if ($sorted) then
			echo		dcm_to_4dfp -b $patid"_t1w" $inpath/study$t1w
			if ($go)	dcm_to_4dfp -b $patid"_t1w" $inpath/study$t1w
		else
			echo		dcm_to_4dfp -b $patid"_t1w" $inpath/$dcmroot.$t1w."*"
			if ($go) 	dcm_to_4dfp -b $patid"_t1w" $inpath/$dcmroot.$t1w.*
		endif
	endif
	echo		t2w2mpr_4dfp $patid"_mpr1" $patid"_t1w" $tarstr
	if ($go)	t2w2mpr_4dfp $patid"_mpr1" $patid"_t1w" $tarstr
	if ($status) exit $status

	echo		epi2t1w_4dfp ${epi_anat} $patid"_t1w" $tarstr
	if ($go)	epi2t1w_4dfp ${epi_anat} $patid"_t1w" $tarstr
	if ($status) exit $status

	echo		t4_mul ${epi_anat}_to_$patid"_t1w_t4" $patid"_t1w_to_"$target:t"_t4"
	if ($go)	t4_mul ${epi_anat}_to_$patid"_t1w_t4" $patid"_t1w_to_"$target:t"_t4"
else if ($ntse) then
	set tselst = ()
	@ k = 1
	while ($k <= $ntse)
		set filenam = $patid"_t2w"
		if ($ntse > 1) set filenam = $filenam$k
		if (! $E4dfp) then
			if ($sorted) then
				echo		dcm_to_4dfp -b $filenam $inpath/study$tse[$k]
				if ($go)	dcm_to_4dfp -b $filenam $inpath/study$tse[$k]
			else
				echo		dcm_to_4dfp -b $filenam $inpath/$dcmroot.$tse[$k]."*"
				if ($go) 	dcm_to_4dfp -b $filenam $inpath/$dcmroot.$tse[$k].*
			endif
			if ($status) exit $status
		endif
		set tselst = ($tselst $filenam)
		@ k++
	end
	if ($ntse  > 1) then
		echo		collate_slice_4dfp $tselst $patid"_t2w"
		if ($go)	collate_slice_4dfp $tselst $patid"_t2w"
	endif
else if (${#pdt2}) then
	if (! $E4dfp) then
		if ($sorted) then
			echo		dcm_to_4dfp -b $patid"_pdt2" $inpath/study$pdt2
			if ($go)	dcm_to_4dfp -b $patid"_pdt2" $inpath/study$pdt2
		else
			echo		dcm_to_4dfp -b $patid"_pdt2" $inpath/$dcmroot.$pdt2."*"
			if ($go) 	dcm_to_4dfp -b $patid"_pdt2" $inpath/$dcmroot.$pdt2.*
		endif
		if ($status) exit $status
	endif
	echo		extract_frame_4dfp $patid"_pdt2" 2 -o$patid"_t2w"
	if ($go)	extract_frame_4dfp $patid"_pdt2" 2 -o$patid"_t2w"
	if ($status) exit $status
endif

@ Et2w = (-e $patid"_t2w".4dfp.img && -e $patid"_t2w".4dfp.ifh)
if ($Et2w) then
#################################################
# if unwarp is needed make sure t2w is transverse
#################################################
	set t2w = $patid"_t2w"
	@ ori = `awk '/orientation/{print $NF}' $patid"_t2w".4dfp.ifh`
	switch ($ori)
	case 2:
		breaksw;
	case 3:
		C2T_4dfp $patid"_t2w"; set t2w = $patid"_t2wT"; breaksw;
	case 4:
		S2T_4dfp $patid"_t2w"; set t2w = $patid"_t2wT"; breaksw;
	default:
		echo $program": illegal $patid"_t2w" orientation"; exit -1; breaksw;
	endsw
	echo		$episcript ${epi_anat} $t2w $patid"_mpr1" useold $tarstr
	if ($go)	$episcript ${epi_anat} $t2w $patid"_mpr1" useold $tarstr
else
	echo		epi2mpr2atl2_4dfp ${epi_anat} $mpr useold $tarstr
	if ($go)	epi2mpr2atl2_4dfp ${epi_anat} $mpr useold $tarstr
endif
if ($status) exit $status

EPI_to_ATL:
if (! $use_anat_ave && $day1_patid == "") then
	/bin/rm ${patid}_anat_ave_to_${target:t}_t4
	ln -s ${patid}_func_vols_ave_to_${target:t}_t4 ${patid}_anat_ave_to_${target:t}_t4
endif

########################################################################
# make atlas transformed epi_anat and t2w in 111 222 and 333 atlas space
########################################################################
set t4file = ${patid}_anat_ave_to_${target:t}_t4
foreach O (111 222 333)
	echo		t4img_4dfp $t4file  ${epi_anat}	${epi_anat}_on_${target:t}_$O -O$O
	if ($go)	t4img_4dfp $t4file  ${epi_anat}	${epi_anat}_on_${target:t}_$O -O$O
	echo		ifh2hdr	 -r2000			${epi_anat}_on_${target:t}_$O
	if ($go)	ifh2hdr	 -r2000			${epi_anat}_on_${target:t}_$O
end
if ($status) exit $status

if ($day1_patid != "" || ! $Et2w) goto SKIPT2W
set t4file = ${t2w}_to_${target:t}_t4
foreach O (111 222 333)
	echo		t4img_4dfp $t4file  ${t2w}	${t2w}_on_${target:t}_$O -O$O
	if ($go)	t4img_4dfp $t4file  ${t2w}	${t2w}_on_${target:t}_$O -O$O
	echo		ifh2hdr	 -r1000			${t2w}_on_${target:t}_$O
	if ($go)	ifh2hdr	 -r1000			${t2w}_on_${target:t}_$O
end
if ($status) exit $status
SKIPT2W:
/bin/rm *t4% >& /dev/null
popd		# out of atlas

UNWARP:
##############################################################
# logic to adjudicate between measured vs. computed field maps
##############################################################
# Let's see what I can do with what I've got
# Avoiding premade scripts because I can
# Assumes spin echo field maps are in pairs
# Assumes pairs positive then negative, i.e. PA, then AP
# which is the order our pairs happen to be collected


# create spin echo field map directory to maybe help alleviate other coding pains later??
# sefm = spin echo field map
# set dwell = 0.51 # already set in the params file
set gre = ""
@ q = 1		# initialize the over arching loop that cycles through all the bold runs
while ( $q <= ${#fstd} ) 	# cycle through each bold run
	# figure out if there is a pair of spin echo field maps that occur before said bold run 
	# but some how flag if the number is too small, i.e. I would want the spin echo field
	# maps that happen right before said bold, not 2 or three before
	# what to do?!  what to do?!  what to do?!  I've got it!  Latrine!
	# ok so here is the "sucky" part about all of this that leads me to hate things a little
	# 1.) I can use this code semi as is and create faux magnitude and phase maps and then
	#	move on with my life
	# 2.) Or I can use a more HCP style approach, so much rejoicing
	# The issue is that both at the end of the day use applywarp versus applytopup because
	# applywarp allows you to do a resampling, thus less smoothing, ever so slightly less
	# but I think it makes things ridiculously harder!!
	# That being said, do I move forward with Qiongru's code or somehow figure out how
	# to loop over all the nonsense that is here by adding my own over arching loop
	# that would do each bold run 1 at a time, then maybe merge together???
	@ qq = ${fstd[$q]}
	# get the line number where the fstd falls within DICOM.studies.txt
	# added extra details because only searching by study number resulted in multiple answers
	###@ p = `cat DICOM.studies.txt | grep -n $qq | awk '{print $1}' | cut -d ":" -f1`
	set frame_counts = `cat "bold"$irun[$q]/$patid"_b"$irun[$q]${MBstr}.4dfp.ifh | grep -F "matrix size [4]" | cut -d "=" -f2`
	set descr = $irun[$q]
	set pre = `echo ${descr} | cut -c1-1`
	if ($pre == "T") then
		set num = `echo ${descr} |cut -c5- `
		set label = fMRI_TASK${num}
	else if ($pre == "A") then
		set num = `echo ${descr} | cut -c13- `
		set label = fMRI_AuditoryTask${num}
	else
		set num = $irun[$q]
		set label = fMRI_REST${num}
	endif
	echo "The label is " $label
	# MM mod 2020-10-23: had to change _90 below to _108; MM update 2021-08-24: had to change it back to 90 for 2.4 slice thickness
   @ p = `cat scans.studies.txt | grep -in ${label} | grep epfid2d1_90 |  grep $frame_counts | grep -i $label| awk '{print $1}' |  cut -d ":" -f1 | head -1`
	echo "Your bold sequence line number is " $p
	# The while loop below is to grab the spin echo field map pairs that happen just previous to the bold run
	# this may be one or more studies prior; in an ideal world this worked and it won't find the first
	# set of spin echo field maps every time or something stupid like that
	while ($p > 0 )
		@ pp = $p - 1	# get the line number prior to the bold data and so forth if needed... haha line below
		set description = `cat scans.studies.txt | awk '{print $2}' | head -$pp | tail -1`	# this will get line(s) prior to bold
		# MM mod: changed it here too
		if ($description == "epse2d1_90" ) then
			# make sure that it is AP or PA; should be AP given our acquistion, but don't ever make asumptions  (2 Ss?)
			set direction = `cat scans.studies.txt | awk '{print $3}' | head -$pp | tail -1 | rev | cut -d "_" -f1 | rev`
			@ ppp = $pp - 1		# get the line before the line. :)  yay pairs
			set direction_line_num = `cat scans.studies.txt | awk '{print $1}' | head -$pp | tail -1`
			set other_direction = `cat scans.studies.txt | awk '{print $3}' | head -$ppp | tail -1 | rev | cut -d "_" -f1 | rev`
			set other_direction_line_num = `cat scans.studies.txt | awk '{print $1}' | head -$ppp | tail -1`
			
			# make sure the directions are indeed PA and AP
			if ($direction == "AP" && $other_direction == "PA" ) then
				#set sefm = ($direction_line_num $other_direction_line_num)
				set sefm = ($other_direction_line_num $direction_line_num)
				echo ""
				echo $sefm
				@ p = 1
				goto ms
			else if ($direction == "PA" && $other_direction == "AP" ) then
				#set sefm = ($other_direction_line_num $direction_line_num)
				set sefm = ($direction_line_num $other_direction_line_num)
				echo ""
				echo $sefm
				@ p = 1
				goto ms
			else
				echo "Error something is jacked up with your sefms"
				exit $p
			endif
		endif
		ms:
		@ p--
		# once the pair is found p will be ultimately set to 0
	end
	# The if statements below give the option for sefm or gre or mean, I took the ones out
	# that don't pertain to spin echo field maps because I feel they are taking up unnecessary
	# space
	# need to alter the sefm statement below so that it will run for each bold run
	#if (${#sefm}) then
	#	if (! -e sefm/${patid}_sefm_mag_brain.nii.gz) then
	#		/data/nil-bluearc/shimony/wunder/wunder_caf_II/wcII_scripts/sefm_pp_AZS_JKK_QYmod.csh ${prmfile} ${instructions} ${sefm[1]} ${sefm[2]}	# creates sefm subdirectory
	#		if ($status) exit $status
	#endif
	if (${#sefm}) then
		if (-d sefm) then
			@ pq = $q - 1
			/bin/mv sefm sefm_${pq}	# this ensures the directory previously make is associated with the correct bold run
						# it does create some redundancies when the same set of spin echo field maps are used
						# but it also allows me to ensure that it was done "right"
						# if we move forward using this code I would like to add logic to get around this particular set
						# of circumstances
			/bin/mv unwarp unwarp_${pq}
			# below iteration of if/else will create the "faux" magnitude/phase for unwarping
			$preproc_scripts_dir/sefm_pp_AZS_JKK_QYmod.csh ${prmfile} ${instructions} ${sefm[1]} ${sefm[2]}	# creates sefm subdirectory
		else
			$preproc_scripts_dir/sefm_pp_AZS_JKK_QYmod.csh ${prmfile} ${instructions} ${sefm[1]} ${sefm[2]}	# creates sefm subdirectory
		endif				
		if ($status) exit $status
	endif
		# Please note that each time a "new" sefm directory is created this is run, this is why this works ok
		set uwrp_args  = (-map $patid atlas/${epi_anat} sefm/${patid}_sefm_mag.nii.gz sefm/${patid}_sefm_pha.nii.gz $dwell $TE_vol $ped 0)
		set log	= ${patid}_fmri_unwarp_170616_se.log
	endif
	##################################
	# compute field mapping correction
	##################################
	date						>! $log
	echo ""
	echo " Wha??? "
	echo ""
	echo	$preproc_scripts_dir/fmri_unwarp_170616_JKK_QYmod.tcsh $uwrp_args	>> $log
		$preproc_scripts_dir/fmri_unwarp_170616_JKK_QYmod.tcsh $uwrp_args	>> $log
	echo ""
	echo "Unwarp complete"
	echo ""

	#####################################
	# rather than change the fmri unwarp code I decided to alter the naming outside for ease
	#####################################
	foreach ending (img ifh hdr img.rec)
		cp unwarp/${epi_anat}_uwrp.4dfp.$ending unwarp/${epi_anat}_uwrp_b${irun[$q]}.4dfp.$ending
	end
	# copy warp file created to individual bold run warp field
	# this will allow the individual warp file fields that were 
	# created to be applied per bold run versus some average
	# probably won't make one lick of difference
	# oddly enough it did make a difference!
	cp unwarp/${epi_anat}_uwrp_shift_warp.nii.gz unwarp/${epi_anat}_uwrp_b${irun[$q]}_shift_warp.nii.gz
	###################################################
	# compute unwarp/${epi_anat}_uwrp_to_${target:t}_t4
	###################################################
echo ${#sefm}
	if (${#sefm} || ${#gre} || ! $?FMbases) then
		if ($Et2w) then
			niftigz_4dfp -n atlas/$t2w atlas/$t2w
			bet atlas/$t2w atlas/${t2w}_brain -m -f 0.4 -R
			niftigz_4dfp -4 atlas/${t2w}_brain_mask atlas/${t2w}_brain_mask -N
			@ mode = 8192 + 2048 + 3
			/bin/cp atlas/${epi_anat}_to_${t2w}_t4 unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${t2w}_t4
			# this imgreg_4dfp is still within each bold run and unwarp hasn't been moved to unwarp_${q}
			imgreg_4dfp atlas/$t2w atlas/${t2w}_brain_mask unwarp/${epi_anat}_uwrp_b${irun[$q]} none unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${t2w}_t4 $mode \
				>! unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${t2w}.log
			if ($status) exit $status

			t4_mul unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${t2w}_t4 atlas/${t2w}_to_${target:t}_t4 unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${target:t}_t4
			if ($status) exit $status
		else
			pushd atlas; msktgen_4dfp $mpr -T$target; popd;
			@ mode = 8192 + 2048 + 3
			/bin/cp atlas/${epi_anat}_to_${mpr}_t4 unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${mpr}_t4
			imgreg_4dfp atlas/${mpr} atlas/${mpr}_mskt unwarp/${epi_anat}_uwrp_b${irun[$q]} none unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${mpr}_t4 $mode \
				>! unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${mpr}.log
			if ($status) exit $status
			t4_mul unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${mpr}_t4 atlas/${mpr}_to_${target:t}_t4 unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${target:t}_t4
			if ($status) exit $status
		endif									unwarp/${epi_anat}_uwrp_on_${struct}
	endif
	foreach O (111 222 333)
		echo		t4img_4dfp unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${target:t}_t4 unwarp/${epi_anat}_uwrp_b${irun[$q]}	unwarp/${epi_anat}_uwrp_b${irun[$q]}_on_${target:t}_$O -O$O
		if ($go)	t4img_4dfp unwarp/${epi_anat}_uwrp_b${irun[$q]}_to_${target:t}_t4 unwarp/${epi_anat}_uwrp_b${irun[$q]}	unwarp/${epi_anat}_uwrp_b${irun[$q]}_on_${target:t}_$O -O$O
		echo		ifh2hdr	 -r2000									unwarp/${epi_anat}_uwrp_b${irun[$q]}_on_${target:t}_$O
		if ($go)	ifh2hdr	 -r2000									unwarp/${epi_anat}_uwrp_b${irun[$q]}_on_${target:t}_$O
	end
	# below if statement ensures that folders are all labeled sequentially
	# versus the last folder created not having a label at the end
	if ($q == ${#fstd} ) then
		/bin/mv sefm "sefm_"$q
		/bin/mv unwarp "unwarp_"$q
	endif
	@ q++
end

####################################################################################################
ATL:
#################################
# one step resample unwarped fMRI
#################################
if (! $epi2atl) exit 0
set x = ${rsam_cmnd:t}; set x = $x:r			# alter one step resampling command to have individual ${epi_anat}_uwrp as reference points, I think
							# that is what Qiongru did, but outside of this code. . . 
set log		= ${patid}_$x.log
date						>! $log
#echo	$rsam_cmnd $prmfile $instructions	>> $log
#	$rsam_cmnd $prmfile $instructions	>> $log
echo	$preproc_scripts_dir/one_step_resample_ind_sef_JKK_ind_BC_QYmod.csh $prmfile $instructions >> $log
	    $preproc_scripts_dir/one_step_resample_ind_sef_JKK_ind_BC_QYmod.csh $prmfile $instructions >> $log
if ($status) exit $status


#################################
# make symbolic links
#################################
@ k = 1
while ($k <= $#irun)
	pushd bold$irun[$k]
	foreach ext(img img.rec ifh hdr)
		echo cp -rus ${patid}_b$irun[$k]${MBstr}_xr3d${BC}_uwrp_atl.4dfp.${ext} ${patid}_b$irun[$k]_xr3d_333.4dfp.${ext}
		cp -rus ${patid}_b$irun[$k]${MBstr}_xr3d${BC}_uwrp_atl.4dfp.${ext} ${patid}_b$irun[$k]_xr3d_333.4dfp.${ext}
	end
	echo cp -rus ${patid}_b$irun[$k]${MBstr}_xr3d.mat ${patid}_b$irun[$k]_xr3d.mat
	cp -rus ${patid}_b$irun[$k]${MBstr}_xr3d.mat ${patid}_b$irun[$k]_xr3d.mat
	@ k++
	popd
end

pushd atlas
foreach ext(img img.rec ifh hdr)
	echo cp -rus ${epi_anat}_on_${target:t}_333.4dfp.${ext} ${patid}_anat_ave_t88_333.4dfp.${ext}
	cp -rus ${epi_anat}_on_${target:t}_333.4dfp.${ext} ${patid}_anat_ave_t88_333.4dfp.${ext}
end
if ($day1_patid != "") then
	foreach ext(img img.rec ifh hdr)
		echo cp -rus $day1_path/${day1_patid}_mpr_n1_333_t88.4dfp.${ext} ${cwd}/${patid}_mpr_n1_333_t88.4dfp.${ext}
		cp -rus $day1_path/${day1_patid}_mpr_n1_333_t88.4dfp.${ext} ${cwd}/${patid}_mpr_n1_333_t88.4dfp.${ext}
	end
endif
popd

exit $status
####################################################################
# remake single resampled 333 atlas space fMRI volumetric timeseries
####################################################################
echo ""
echo bold$irun[$k]/${patid}_b$irun[$k]${MBstr}_xr3d${BC}_uwrp_atl.4dfp.img
echo ""
echo "broke here0"
echo ""
set lst = ${patid}${MBstr}_xr3d${BC}_uwrp_atl.lst
if (-e $lst) /bin/rm $lst
touch $lst
@ k = 1
echo ""
echo bold$irun[$k]/${patid}_b$irun[$k]${MBstr}_xr3d${BC}_uwrp_atl.4dfp.img
echo ""
echo "broke here1"
echo ""
#while ($k <= $#irun)
#	echo bold$irun[$k]/${patid}_b$irun[$k]${MBstr}_xr3d_uwrp_atl.4dfp.img >> $lst
#	@ k++
#end
while ($k <= $#irun)
	echo bold$irun[$k]/${patid}_b$irun[$k]${MBstr}_xr3d${BC}_uwrp_atl.4dfp.img >> $lst
	@ k++
end
echo ""
echo bold$irun[$k]/${patid}_b$irun[$k]${MBstr}_xr3d${BC}_uwrp_atl.4dfp.img
echo ""
echo "broke here2"
echo ""
conc_4dfp ${lst:r}.conc -l$lst
if ($status) exit $status
set fmtfile = atlas/${patid}_func_vols.format
if (! -e $fmtfile) exit $status
actmapf_4dfp $fmtfile ${patid}${MBstr}_xr3d${BC}_uwrp_atl.conc -aave
if ($status) exit $status
ifh2hdr -r2000 		${patid}${MBstr}_xr3d${BC}_uwrp_atl_ave
mv			${patid}${MBstr}_xr3d${BC}_uwrp_atl_ave.4dfp.*	atlas
var_4dfp -sF$fmtfile	${patid}${MBstr}_xr3d${BC}_uwrp_atl.conc
ifh2hdr -r20		${patid}${MBstr}_xr3d${BC}_uwrp_atl_sd1
mv			${patid}${MBstr}_xr3d${BC}_uwrp_atl_sd1*		atlas
mv			${patid}${MBstr}_xr3d${BC}_uwrp_atl.conc*		atlas

echo $program complete
exit 0



