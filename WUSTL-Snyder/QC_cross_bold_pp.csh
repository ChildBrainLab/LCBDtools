#!/bin/csh

# prmfile is taking in the patient id and QC dir
set prmfile = $1
source $cwd/$prmfile
set QCdir = $2
set scriptdir = /data/nil-bluearc/raichle/lin64-tools
if (! ${?day1_patid}) then
	pushd atlas
	tal_QC_AZS ${patid}_mpr1_to_TRIO_KY_NDC.log >! $QCdir/${patid}_tal_QC_AZS.log
	cat ${patid}_mpr1_epi2t2w2mpr2atl2_4dfp.log | gawk -f ${scriptdir}/parse_epi2i2w2mpr2atl2_log.awk >! $QCdir/${patid}_epi2i2w2mpr2atl2.log
	popd
endif

