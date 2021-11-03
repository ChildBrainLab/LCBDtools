#!/bin/csh -x

set program = $0; set program = $program:t
if (${#argv} < 1) then
	echo "Usage:	"$program" <patid>"
	echo "e.g.,	"$program" neo339a"
	exit 1
endif
set patid = $1
if (! -d $patid) then
	echo $patid not a directory
	exit -1
endif

pushd $patid
source $patid.params
@ num_bolds = ${#fstd}
echo num_bolds=$num_bolds
popd

if ($BiasField) then
	set BC = "_BC"
	echo "BC is "$BC
else
	set BC = ""
endif
echo "here"
if (! ${?MB}) @ MB = 0			# skip slice timing correction and debanding
set MBstr = _faln_dbnd
if ($MB) set MBstr = ""
echo $MB
echo $MBstr
echo "stuff"
@ i = 1
while ($i <= $num_bolds) 
	pushd $patid/bold$i #into $patid/bold$i
	if ($status) exit $status
	conc_4dfp ${patid}'_b'$i${MBstr}'_xr3d'${BC}'_uwrp_atl' ${patid}'_b'$i${MBstr}'_xr3d'${BC}'_uwrp_atl'.4dfp.img
	run_dvar_4dfp ${patid}'_b'$i${MBstr}'_xr3d'${BC}'_uwrp_atl'.conc -m$REFDIR/glm_atlas_mask_333 -n$skip -x50
	if ($status) exit $status
	set format = `more ${patid}'_b'$i${MBstr}'_xr3d'${BC}'_uwrp_atl'.format`
echo "one"
	echo format=$format
	popd			# out of $patid/bold$i
	@ i++
end

pushd $patid
if ( -e ${patid}_conc.lst ) then
	/bin/rm ${patid}_conc.lst
endif

foreach run ($fcbolds)
echo "two"
pwd
	echo set file = $srcdir/bold$run/*${MBstr}*xr3d${BC}_uwrp_atl.4dfp.img
	set file = $srcdir/bold$run/*${MBstr}*xr3d${BC}_uwrp_atl.4dfp.img
	echo $file >> ${patid}_conc.lst
end

conc_4dfp ${patid}${MBstr}_xr3d${BC}_uwrp_atl -l${patid}_conc.lst -w

run_dvar_4dfp ${patid}${MBstr}_xr3d${BC}_uwrp_atl.conc -m$REFDIR/glm_atlas_mask_333 -n$skip -x50

if ($status) exit $status
pwd
echo "three"
set format = `more ${patid}${MBstr}_xr3d${BC}_uwrp_atl.format`
echo format=$format

if (! -e QA) mkdir QA
/bin/mv ${patid}${MBstr}_xr3d${BC}_uwrp_atl.format ./QA

/bin/mv ${patid}${MBstr}_xr3d${BC}_uwrp_atl.* ./QA
if ($status) exit $status

popd
exit
